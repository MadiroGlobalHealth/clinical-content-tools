fn(state => {
  // Function to generate base URLs based on environment name
  const getBaseUrls = (environment) => {
    const baseUrl = `http://${environment}.madiro.org/openmrs/ws/rest/v1`;
    return {
      concepts: `${baseUrl}/concept/`,
      attributes: `${baseUrl}/personattributetype/`,
      identifiers: `${baseUrl}/patientidentifiertype/`
    };
  };
  
  // Extract environment name from the state or use a parameter
  const environment = state.environment || 'lime-mosul-uat';
  const environmentDisplay = environment.includes('-') ? 
    environment.split('-').map(part => part.charAt(0).toUpperCase() + part.slice(1)).join('-') :
    environment.toUpperCase();
  
  // Generate base URLs for the current environment
  const baseUrls = getBaseUrls(environment);
  
  const concepts = state.concepts;
  const attributes = state.attributes;
  const identifiers = state.identifiers;
  
  // Initialize simplified statistics object (combining notFound and error)
  const statistics = {
    concepts: { total: Object.keys(concepts).length, found: 0, missing: 0 },
    attributes: { total: Object.keys(attributes).length, found: 0, missing: 0 },
    identifiers: { total: Object.keys(identifiers).length, found: 0, missing: 0 },
    get total() { 
      return this.concepts.total + this.attributes.total + this.identifiers.total;
    },
    get totalFound() { 
      return this.concepts.found + this.attributes.found + this.identifiers.found;
    },
    get totalMissing() { 
      return this.concepts.missing + this.attributes.missing + this.identifiers.missing;
    }
  };
  
  // Helper function to check an entity against an API endpoint and update statistics
  const checkEntity = (uuid, entity, entityType) => {
    // Initialize the statuses object if it doesn't exist
    if (!entity.statuses) {
      entity.statuses = {};
    }
    
    return fn(state => 
      get(`${baseUrls[entityType]}${uuid}`, {
        headers: { 'Content-Type': 'application/json' },
        throwHttpErrors: false
      })(state).then(state => {
        if (state.response.statusCode === 200) {
          entity.statuses[environmentDisplay] = 'Found';
          statistics[entityType].found++;
        } else {
          entity.statuses[environmentDisplay] = 'Missing';
          statistics[entityType].missing++;
        }
        return entity;
      }).catch(error => {
        console.error(`Error checking ${entityType} ${uuid} in ${environment}:`, error);
        entity.statuses[environmentDisplay] = 'Missing';
        statistics[entityType].missing++;
        return entity;
      })
    );
  };
  
  // Check concepts
  const conceptChecks = Object.entries(concepts).map(([uuid, concept]) => {
    return checkEntity(uuid, concept, 'concepts');
  });
  
  // Check attributes
  const attributeChecks = Object.entries(attributes).map(([uuid, attr]) => {
    return checkEntity(uuid, attr, 'attributes');
  });
  
  // Check identifiers
  const identifierChecks = Object.entries(identifiers).map(([uuid, ident]) => {
    return checkEntity(uuid, ident, 'identifiers');
  });
  
  // Combine all checks
  const allChecks = [...conceptChecks, ...attributeChecks, ...identifierChecks];
  
  return fn(state =>
    Promise.all(allChecks.map(operation => operation(state)))
  )(state).then(updatedEntities => {
    // Split the results back into their respective categories
    const conceptsCount = Object.keys(concepts).length;
    const attributesCount = Object.keys(attributes).length;
    
    const updatedConcepts = updatedEntities.slice(0, conceptsCount);
    const updatedAttributes = updatedEntities.slice(
      conceptsCount, 
      conceptsCount + attributesCount
    );
    const updatedIdentifiers = updatedEntities.slice(
      conceptsCount + attributesCount
    );
    
    // Convert back to objects with UUIDs as keys
    const updatedConceptsObj = Object.keys(concepts).reduce((acc, uuid, index) => {
      acc[uuid] = updatedConcepts[index];
      return acc;
    }, {});
    
    const updatedAttributesObj = Object.keys(attributes).reduce((acc, uuid, index) => {
      acc[uuid] = updatedAttributes[index];
      return acc;
    }, {});
    
    const updatedIdentifiersObj = Object.keys(identifiers).reduce((acc, uuid, index) => {
      acc[uuid] = updatedIdentifiers[index];
      return acc;
    }, {});
    
    // Initialize or update the environmentStats structure
    if (!state.environments) {
      state.environments = {};
    }
    
    // Store environment-specific stats in a dedicated object
    state.environments[environment] = {
      display: environmentDisplay,
      timestamp: new Date().toISOString(),
      stats: {
        concepts: { ...statistics.concepts },
        attributes: { ...statistics.attributes },
        identifiers: { ...statistics.identifiers },
        summary: {
          total: statistics.total,
          found: statistics.totalFound,
          missing: statistics.totalMissing,
          foundPercentage: Math.round((statistics.totalFound / statistics.total) * 100) + '% ✅',
          missingPercentage: Math.round((statistics.totalMissing / statistics.total) * 100) + '% ❌'
        }
      }
    };
    
    return { 
      ...state, 
      environment,
      concepts: updatedConceptsObj,
      attributes: updatedAttributesObj,
      identifiers: updatedIdentifiersObj,
      environments: state.environments
    };
  });
});
fn(state => {
  delete state.references;
});
