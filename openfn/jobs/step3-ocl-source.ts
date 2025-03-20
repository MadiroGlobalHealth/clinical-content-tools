fn(state => {
    console.log('Starting OCL verification job');
    
    // Validate that required data exists
    if (!state.conceptUUIDs || !Array.isArray(state.conceptUUIDs)) {
      console.error('Error: conceptUUIDs is missing or not an array');
      return { ...state, error: 'conceptUUIDs is missing or not an array' };
    }
    
    if (!state.processedForms || typeof state.processedForms !== 'object') {
      console.error('Error: processedForms is missing or not an object');
      return { ...state, error: 'processedForms is missing or not an object' };
    }
    
    console.log(`Starting OCL verification for ${state.conceptUUIDs.length} concepts`);
    
    // OCL API base URL for MSF organization
    const baseUrl = 'https://api.openconceptlab.org/orgs/MSF/sources/MSF/concepts';
    const environment = 'OCL-Source';
    
    // Initialize statistics
    state.statistics = state.statistics || {};
    state.statistics[environment] = {
      total: state.conceptUUIDs.length,
      found: 0,
      missing: 0
    };
    
    // Helper function to check a concept against the OCL API
    const checkConcept = (uuid) => {
      return fn(state => 
        // Using a query parameter to search for the UUID
        get(`${baseUrl}?q=${uuid}`, {
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
          
          // Update concept status in processedForms
          Object.keys(state.processedForms).forEach(formKey => {
            const questions = state.processedForms[formKey];
            if (Array.isArray(questions)) {
              questions.forEach(question => {
                if (question.externalId && question.externalId.value === uuid) {
                  question.externalId[environment] = found ? 'Found' : 'Missing';
                }
                
                if (question.answers && Array.isArray(question.answers)) {
                  question.answers.forEach(answer => {
                    if (answer.externalId && answer.externalId.value === uuid) {
                      answer.externalId[environment] = found ? 'Found' : 'Missing';
                    }
                  });
                }
              });
            }
          });
          
          // Update statistics
          state.statistics[environment][found ? 'found' : 'missing']++;
          
          console.log(`Concept ${uuid} ${found ? 'found' : 'missing'} in OCL`);
          return state;
        }).catch(error => {
          console.error(`Error checking concept ${uuid} in ${environment}:`, error);
          
          // Update concept status in processedForms as missing due to error
          Object.keys(state.processedForms).forEach(formKey => {
            const questions = state.processedForms[formKey];
            if (Array.isArray(questions)) {
              questions.forEach(question => {
                if (question.externalId && question.externalId.value === uuid) {
                  question.externalId[environment] = 'Missing';
                }
                
                if (question.answers && Array.isArray(question.answers)) {
                  question.answers.forEach(answer => {
                    if (answer.externalId && answer.externalId.value === uuid) {
                      answer.externalId[environment] = 'Missing';
                    }
                  });
                }
              });
            }
          });
          
          state.statistics[environment].missing++;
          return state;
        })
      );
    };
    
    // Create array of check operations for all concepts
    const conceptChecks = state.conceptUUIDs.map(uuid => checkConcept(uuid));
    
    // Execute all checks in sequence
    return conceptChecks.reduce(
      (acc, check) => acc.then(state => check(state)),
      Promise.resolve(state)
    ).then(state => {
      console.log('OCL verification completed');
      console.log(`Total: ${state.statistics[environment].total}`);
      console.log(`Found: ${state.statistics[environment].found}`);
      console.log(`Missing: ${state.statistics[environment].missing}`);
      
      // Initialize meta if it doesn't exist
      state.meta = state.meta || {};
      
      // Add environment and timestamp to meta
      state.meta[environment] = new Date().toISOString();
      
      return state;
    });
  });
  
  fn(state => {
    delete state.data;
    delete state.references;
    return state;
  });