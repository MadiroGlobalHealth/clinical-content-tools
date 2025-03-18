// --------------------------------------------------------------------
// 1. Group and Enrich UUIDs, and Initialize Statistics
// --------------------------------------------------------------------
fn(state => {
  // Initialize groups to hold enriched UUID objects.
  state.concepts = [];
  state.personattributetypes = [];
  state.identifiersVerified = [];

  // Process formMaps for concepts (all keys except "patient")
  if (state.formMaps && typeof state.formMaps === 'object') {
    Object.keys(state.formMaps).forEach(formKey => {
      if (formKey !== "patient") {
        const form = state.formMaps[formKey];
        if (form.dataValueMap && typeof form.dataValueMap === 'object') {
          Object.keys(form.dataValueMap).forEach(dataKey => {
            const uuid = form.dataValueMap[dataKey];
            console.log("Processing Concept UUID:", uuid);
            state.concepts.push({
              uuid: uuid,
              status: "Not Checked"
            });
          });
        }
      }
    });

    // Process patient key for personattributetypes
    if (state.formMaps.patient && state.formMaps.patient.dataValueMap) {
      Object.keys(state.formMaps.patient.dataValueMap).forEach(dataKey => {
        const uuid = state.formMaps.patient.dataValueMap[dataKey];
        console.log("Processing Person Attribute Type UUID:", uuid);
        state.personattributetypes.push({
          uuid: uuid,
          status: "Not Checked"
        });
      });
    }
  } else {
    console.log("No valid formMaps found.");
  }

  // Process the identifiers array to extract identifier UUIDs from "omrs identifierType"
  if (Array.isArray(state.identifiers)) {
    state.identifiers.forEach(identifier => {
      if (identifier["omrs identifierType"]) {
        const uuid = identifier["omrs identifierType"];
        console.log("Processing Identifier UUID:", uuid);
        state.identifiersVerified.push({
          uuid: uuid,
          status: "Not Checked"
        });
      }
    });
  } else {
    console.log("No valid identifiers found.");
  }

  // Initialize statistics for each group.
  state.statistics = {
    concepts: {
      total: state.concepts.length,
      notChecked: state.concepts.length,
      found: 0,
      notFound: 0
    },
    personattributetypes: {
      total: state.personattributetypes.length,
      notChecked: state.personattributetypes.length,
      found: 0,
      notFound: 0
    },
    identifiers: {
      total: state.identifiersVerified.length,
      notChecked: state.identifiersVerified.length,
      found: 0,
      notFound: 0
    }
  };

  return state;
});

// --------------------------------------------------------------------
// 2. Log and Verify each Concept UUID via API
// --------------------------------------------------------------------
fn(state => {
  console.log("Starting concept verification. Total number of concepts to check:", state.concepts.length);
  return state;
});

each(
  '$.concepts[*]',
  get(`concept/${$.data.uuid}`)
    .then(state => {
      // Find the concept in the parent array and update its status
      const index = state.concepts.findIndex(concept => concept.uuid === state.data.uuid);
      if (index !== -1) {
        state.concepts[index].status = "Found";
      }
      state.statistics.concepts.found += 1;
      state.statistics.concepts.notChecked -= 1;
      console.log(`Concept ${state.data.uuid} verified: Found`);
      return state;
    })
    .catch((error, state) => {
      // On error, update the corresponding concept's status
      const index = state.concepts.findIndex(concept => concept.uuid === state.data.uuid);
      if (index !== -1) {
        state.concepts[index].status = "Not Found";
      }
      state.statistics.concepts.notFound += 1;
      state.statistics.concepts.notChecked -= 1;
      console.log(`Concept ${state.data.uuid} error: ${state.response.statusCode}`);
      return state;
    })
);

// --------------------------------------------------------------------
// 3. Log and Verify each Person Attribute Type UUID via API
// --------------------------------------------------------------------
fn(state => {
  console.log("Starting person attribute type verification. Total number of attributes to check:", state.personattributetypes.length);
  if (!state.personattributetypes) {
    console.log('Warning: personattributetypes is not defined in state');
    return state;
  }
  return state;
});

each(
  '$.personattributetypes[*]',
  get(`personattributetype/${$.data.uuid}`)
    .then(state => {
      // Find the concept in the parent array and update its status
      const index = state.personattributetypes.findIndex(attribute => attribute.uuid === state.data.uuid);
      if (index !== -1) {
        state.personattributetypes[index].status = "Found";
      }
      state.statistics.personattributetypes.found += 1;
      state.statistics.personattributetypes.notChecked -= 1;
      console.log(`Attribute ${state.data.uuid} verified: Found`);
      return state;
    })
    .catch((error, state) => {
      // On error, update the corresponding attribute's status
      const index = state.personattributetypes.findIndex(attribute => attribute.uuid === state.data.uuid);
      if (index !== -1) {
        state.personattributetypes[index].status = "Not Found";
      }
      state.statistics.personattributetypes.notFound += 1;
      state.statistics.personattributetypes.notChecked -= 1;
      console.log(`Attribute ${state.data.uuid} error: ${state.response.statusCode}`);
      return state;
    })
);

// --------------------------------------------------------------------
// 4. Log and Verify each Identifier UUID via API
// --------------------------------------------------------------------
fn(state => {
  console.log("Starting identifier verification. Total number of identifiers to check:", state.identifiersVerified.length);
  return state;
});

each(
  '$.identifiersVerified[*]',
  get(`patientidentifiertype/${$.data.uuid}`)
    .then(state => {
      const index = state.identifiersVerified.findIndex(ident => ident.uuid === state.data.uuid);
      if (index !== -1) {
        state.identifiersVerified[index].status = "Found";
      }
      state.statistics.identifiers.found += 1;
      state.statistics.identifiers.notChecked -= 1;
      console.log(`Identifier ${state.data.uuid} verified: Found`);
      return state;
    })
    .catch((error, state) => {
      const index = state.identifiersVerified.findIndex(ident => ident.uuid === state.data.uuid);
      if (index !== -1) {
        state.identifiersVerified[index].status = "Not Found";
      }
      state.statistics.identifiers.notFound += 1;
      state.statistics.identifiers.notChecked -= 1;
      console.log(`Identifier ${state.data.uuid} error: ${state.response.statusCode}`);
      return state;
    })
);

// --------------------------------------------------------------------
// 5. Filter and Sort the State Object
// --------------------------------------------------------------------
fn(state => {
  const sortedState = {
    identifiers: state.identifiersVerified || [],
    attributes: state.personattributetypes || [],
    concepts: state.concepts || [],
    statistics: state.statistics || {}
  };
  return sortedState;
});


