  // --------------------------------------------------------------------
  // 2. Log and Verify each Concept UUID via API
  // --------------------------------------------------------------------
  fn(state => {

    state.allConceptIds = Object.keys(state.concepts)
    // state.allConceptIds = ['401b2df0-e26f-4f49-9165-6e20a1b8865a']
    console.log("Starting concept verification. Total number of concepts to check:", state.allConceptIds.length);
    return state;
  });

each(
  $.allConceptIds,
  get(`concept/${$.data}`)
    .catch((error, state) => {
        // pull the uuid out of the error url
      const uuidMatch =  error.message.match(/([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})/)
      if (uuidMatch) {
        const uuid = uuidMatch[0]
        
        // Update the status
        state.concepts[uuid].statuses['EMR-UAT'] = "Not Found";

        state.statistics.concepts.emrNotFound += 1;
        state.statistics.concepts.notChecked -= 1;
        console.log(`concept ${uuid} not found`);
      } else {
        console.log('UNEXPECTED UUID:')
        console.log(error)
      }
      return state;
    })
    .then((state) => {
      // Lookup the previous state.data (before the get to get our uuid)
      const uuid = state.references.at(-1)

      // workaround possible broken promise :'(
      if (uuid && !state.concepts[uuid].statuses['EMR-UAT']) {
        // Update the status
        state.concepts[uuid].statuses['EMR-UAT'] = "Found";

        state.statistics.concepts.emrFound += 1;
        state.statistics.concepts.notChecked -= 1;
        console.log(`concept ${uuid} found`);
      }
      return state;
    })
);

  fn(state => {
    console.log("Starting attributes verification. Total number of attributes to check:", state.attributes.length);
    return state;
  });

  each(
    '$.attributes[*]',
    get(`personattributetype/${$.data.uuid}`)
      .catch((error, state) => {
        // On error, update the corresponding concept's status
        const index = state.attributes.findIndex(attribute => attribute.uuid === state.data.uuid);
        if (index !== -1) {
          state.attributes[index].emrStatus = "Not Found";
        }
        state.statistics.personattributetypes.emrNotFound += 1;
        state.statistics.personattributetypes.notChecked -= 1;
        console.log(`attribute ${state.data.uuid} not found`);
        return state;
      })

      .then(state => {
        // First find the attribute        
        const targetId = state.data.uuid
        const attribute = state.attributes.find(attribute => attribute.uuid === targetId);
        // This will fire even after a catch, so first check this item didn't error
        if (attribute.emrStatus !== "Not Found") {
          state.statistics.personattributetypes.emrFound += 1;
          state.statistics.personattributetypes.notChecked -= 1;
          attribute.emrStatus = "Found";
          console.log(`attribute ${attribute.uuid} verified: Found`);
        }
        return state;
      })
  );

  fn(state => {
    console.log("Starting identifiers verification. Total number of identifiers to check:", state.identifiers.length);
    return state;
  });

  each(
    '$.identifiers[*]',
    get(`patientidentifiertype/${$.data.uuid}`)
      .catch((error, state) => {
        // On error, update the corresponding concept's status
        const index = state.identifiers.findIndex(identifier => identifier.uuid === state.data.uuid);
        if (index !== -1) {
          state.identifiers[index].emrStatus = "Not Found";
        }
        state.statistics.patientidentifiertypes.emrNotFound += 1;
        state.statistics.patientidentifiertypes.notChecked -= 1;
        console.log(`identifier ${state.data.uuid} not found`);
        return state;
      })

      .then(state => {
        // First find the identifier        
        const targetId = state.data.uuid
        const identifier = state.identifiers.find(identifier => identifier.uuid === targetId);
        // This will fire even after a catch, so first check this item didn't error
        if (identifier.emrStatus !== "Not Found") {
          state.statistics.patientidentifiertypes.emrFound += 1;
          state.statistics.patientidentifiertypes.notChecked -= 1;
          identifier.emrStatus = "Found";
          console.log(`identifier ${identifier.uuid} verified: Found`);
        }
        return state;
      })
  );


  fn(state => {
    delete state.allConceptIds
    return state;
  });
