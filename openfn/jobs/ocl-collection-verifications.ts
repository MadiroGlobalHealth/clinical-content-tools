fn(state => {
  // OCL API base URL for MSF organization
  const getOclUrl = () => {
    return 'https://api.openconceptlab.org/orgs/MSFOCG/collections/iraq-mosul/concepts/';
  };
  
  // Single environment name variable
  const environment = 'OCL-MSFOCG-IraqMosul';
  
  // OCL base URL
  const oclBaseUrl = getOclUrl();
  
  const concepts = state.concepts;
  const attributes = state.attributes;
  
  // Initialize simplified statistics object
  const statistics = {
    concepts: { total: Object.keys(concepts).length, found: 0, missing: 0 },
    attributes: { total: Object.keys(attributes).length, found: 0, missing: 0 },
    get total() { 
      return this.concepts.total + this.attributes.total;
    },
    get totalFound() { 
      return this.concepts.found + this.attributes.found;
    },
    get totalMissing() { 
      return this.concepts.missing + this.attributes.missing;
    }
  };
  
  // Helper function to check an entity against the OCL API endpoint and update statistics
  const checkEntity = (uuid, entity, entityType) => {
    // Initialize the statuses object if it doesn't exist
    if (!entity.statuses) {
      entity.statuses = {};
    }
    
    return fn(state => 
      // Using a query parameter to search for the UUID
      get(`${oclBaseUrl}?q=${uuid}`, {
        headers: { 'Content-Type': 'application/json' },
        throwHttpErrors: false
      })(state).then(state => {
        let found = false;
        
        // Check if response is valid and contains data
        if (state.response.statusCode === 200) {          
          // Look through all results to find matching external_id
          found = state.data.some(item => item.external_id === uuid);
        } else {
          console.log(`Non-200 response for ${uuid}:`, state.response.statusCode);
        }
        
        // Update entity status and statistics
        entity.statuses[environment] = found ? 'Found' : 'Missing';
        statistics[entityType][found ? 'found' : 'missing']++;
        
        return entity;
      }).catch(error => {
        console.error(`Error checking ${entityType} ${uuid} in ${environment}:`, error);
        entity.statuses[environment] = 'Missing';
        statistics[entityType].missing++;
        return entity;
      })
    );
  };
  
  // Create arrays of check operations for concepts and attributes
  const conceptChecks = Object.entries(concepts).map(([uuid, concept]) => 
    checkEntity(uuid, concept, 'concepts'));
  
  const attributeChecks = Object.entries(attributes).map(([uuid, attr]) => 
    checkEntity(uuid, attr, 'attributes'));
  
  // Combine all checks
  const allChecks = [...conceptChecks, ...attributeChecks];
  
  return fn(state =>
    Promise.all(allChecks.map(operation => operation(state)))
  )(state).then(updatedEntities => {
    // Split the results back into their respective categories
    const conceptsCount = Object.keys(concepts).length;
    
    // Convert arrays back to objects with UUIDs as keys
    const updatedConceptsObj = Object.keys(concepts).reduce((acc, uuid, index) => {
      acc[uuid] = updatedEntities[index];
      return acc;
    }, {});
    
    const updatedAttributesObj = Object.keys(attributes).reduce((acc, uuid, index) => {
      acc[uuid] = updatedEntities[index + conceptsCount];
      return acc;
    }, {});
    
    // Initialize environments object if it doesn't exist
    if (!state.environments) {
      state.environments = {};
    }
    
    // Calculate percentages
    const foundPercentage = Math.round((statistics.totalFound / statistics.total) * 100);
    const missingPercentage = Math.round((statistics.totalMissing / statistics.total) * 100);
    
    // Store environment-specific stats
    state.environments[environment] = {
      display: environment,
      timestamp: new Date().toISOString(),
      stats: {
        concepts: { ...statistics.concepts },
        attributes: { ...statistics.attributes },
        summary: {
          total: statistics.total,
          found: statistics.totalFound,
          missing: statistics.totalMissing,
          foundPercentage: `${foundPercentage}% ✅`,
          missingPercentage: `${missingPercentage}% ❌`
        }
      }
    };
    
    return { 
      ...state, 
      environment,
      concepts: updatedConceptsObj,
      attributes: updatedAttributesObj,
      environments: state.environments
    };
  });
});
