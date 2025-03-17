// --------------------------------------------------------------------
// 1. Group and Enrich UUIDs
// --------------------------------------------------------------------
fn(state => {
  // Initialize groups to hold enriched UUID objects
  state.project = "Iraq";
  state.projectID = "6d9cddc4-802f-48a6-bddc-7d2038c5fa92";
  state.forms = {};
  state.personattributetypes = {};
  state.patientidentifiertypes = {};
  state.concepts = {};

  // Process forms and concepts
  if (state.formMaps && typeof state.formMaps === 'object') {
    Object.entries(state.formMaps).forEach(([formKey, formEntry]) => {
      // Process valid dataValueMap entries
      if (formEntry?.dataValueMap && typeof formEntry.dataValueMap === 'object') {
        const formName = formEntry.formName || formKey;
        
        // Initialize form array
        if (!state.forms[formName]) {
          state.forms[formName] = [];
        }
        
        // Process concept UUIDs
        Object.values(formEntry.dataValueMap).forEach(uuid => {
          state.concepts[uuid] ??= { forms: [] };
          state.concepts[uuid].forms.push(formName);
        });
      }
    });
  
    // Process patient attributes (special case)
    if (state.formMaps.patient?.dataValueMap) {
      Object.values(state.formMaps.patient.dataValueMap).forEach(uuid => {
        state.personattributetypes[uuid] ??= {};
      });
    }
  }

  // Process patient identifier types
  if (Array.isArray(state.identifiers)) {
    state.identifiers.forEach(identifier => {
      const uuid = identifier["omrs identifierType"];
      if (uuid) {
        state.patientidentifiertypes[uuid] ??= {};
      }
    });
  }

  return state;
});

// --------------------------------------------------------------------
// 2. Filter and Sort the State Object with Renamed Properties
// --------------------------------------------------------------------
fn(state => {
  const sortedState = {
    concepts: state.concepts || {},
    attributes: state.personattributetypes || {},    // Renamed from personattributetypes
    identifiers: state.patientidentifiertypes || {}, // Renamed from patientidentifiertypes
    project: state.project || [],
    projectID: state.projectID || [],
    forms: state.forms || {},
    fileDateModified: state.fileDateModified || {},
    syncedAt: state.syncedAt || {},
    sourceFile: state.sourceFile || {}
  };
  return sortedState;
});

// --------------------------------------------------------------------
// 3. Remove Forms from State
// --------------------------------------------------------------------
fn(state => {
  delete state.forms;
  return state;
});
