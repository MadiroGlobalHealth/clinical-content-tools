fn(state => {
  // Initialize structure to hold processed forms
  const processedForms = {};
  const optionSets = {};
  const conceptUUIDs = []; // Array to collect all external IDs
  
  // Create meta object with required fields
  const meta = {
    folderPath: state.folderPath || null,
    lastSync: state.lastSync || null,
    siteName: state.siteName || null,
    syncedAt: state.syncedAt || new Date().toISOString(),
    projectID: 9 // Hardcoded as requested
  };
  
  // Helper function to create value objects
  const createValueObj = (value) => {
    return value ? { value } : null;
  };
  
  // First pass: extract all option sets for lookup
  if (state.OptionSets && Array.isArray(state.OptionSets)) {
    // Find header row and column indices
    const optionSetHeaders = state.OptionSets.find(row => 
      row && row.includes("OptionSet name") && row.includes("Answers") && row.includes("External ID"));
    
    if (optionSetHeaders) {
      const optionSetNameIndex = optionSetHeaders.indexOf("OptionSet name");
      const answerIndex = optionSetHeaders.indexOf("Answers");
      const translationIndex = optionSetHeaders.indexOf("Translation");
      const externalIdIndex = optionSetHeaders.indexOf("External ID");
      const dhis2OptionUidIndex = optionSetHeaders.indexOf("DHIS2 Option UID");
      
      // Process option sets data (skip header rows)
      const headerRowIndex = state.OptionSets.indexOf(optionSetHeaders);
      const optionSetData = state.OptionSets.slice(headerRowIndex + 1);
      
      optionSetData.forEach(row => {
        if (!row || row.length <= Math.max(optionSetNameIndex, answerIndex, externalIdIndex)) return;
        
        const optionSetName = row[optionSetNameIndex];
        const answer = row[answerIndex];
        const translation = (translationIndex >= 0) ? row[translationIndex] : null;
        const externalId = row[externalIdIndex];
        const dhis2OptionUid = (dhis2OptionUidIndex >= 0) ? row[dhis2OptionUidIndex] : null;
        
        if (!optionSetName || !answer) return;
        
        // Add externalId to conceptUUIDs if it exists and is not already in the array
        if (externalId && !conceptUUIDs.includes(externalId)) {
          conceptUUIDs.push(externalId);
        }
        
        if (!optionSets[optionSetName]) {
          optionSets[optionSetName] = [];
        }
        
        // Order properties as requested
        optionSets[optionSetName].push({
          answer: createValueObj(answer),
          translation: createValueObj(translation),
          externalId: createValueObj(externalId),
          dhis2OptionUid: createValueObj(dhis2OptionUid)
        });
      });
    }
  }
  
  // Second pass: process forms and their questions
  Object.keys(state).forEach(key => {
    // Only process form arrays (keys starting with F followed by digits)
    if (key.match(/^F\d+/) && Array.isArray(state[key])) {
      const formData = state[key];
      
      // Find header row and column indices
      const formHeaders = formData.find(row => 
        row && row.includes("Question") && row.includes("External ID") && row.includes("Datatype"));
      
      if (formHeaders) {
        const questionIndex = formHeaders.indexOf("Question");
        const translationQuestionIndex = formHeaders.indexOf("Translation - Question");
        const datatypeIndex = formHeaders.indexOf("Datatype");
        const externalIdIndex = formHeaders.indexOf("External ID");
        const dhis2DeUidIndex = formHeaders.indexOf("DHIS2 DE UID");
        const optionSetNameIndex = formHeaders.indexOf("OptionSet name");
        
        // Process form data (skip header row)
        const headerRowIndex = formData.indexOf(formHeaders);
        const questionData = formData.slice(headerRowIndex + 1);
        
        // Initialize form with empty questions array
        processedForms[key] = [];
        
        questionData.forEach(row => {
          if (!row || row.length <= Math.max(questionIndex, externalIdIndex)) return;
          
          const question = row[questionIndex];
          const translation = (translationQuestionIndex >= 0) ? row[translationQuestionIndex] : null;
          const datatype = (datatypeIndex >= 0) ? row[datatypeIndex] : null;
          const externalId = row[externalIdIndex];
          const dhis2DeUid = (dhis2DeUidIndex >= 0) ? row[dhis2DeUidIndex] : null;
          const optionSetName = optionSetNameIndex >= 0 ? row[optionSetNameIndex] : null;
          
          if (!question || !externalId) return;
          
          // Add externalId to conceptUUIDs if it's not already in the array
          if (!conceptUUIDs.includes(externalId)) {
            conceptUUIDs.push(externalId);
          }
          
          // Create question object with properties in the requested order
          const questionObj = {
            question: createValueObj(question),
            translation: createValueObj(translation),
            datatype: createValueObj(datatype),
            externalId: createValueObj(externalId),
            dhis2DeUid: createValueObj(dhis2DeUid)
          };
          
          // Only add answers if this question has an option set with answers
          if (optionSetName && optionSets[optionSetName] && optionSets[optionSetName].length > 0) {
            questionObj.answers = optionSets[optionSetName];
            questionObj.optionSetName = createValueObj(optionSetName);
          }
          
          processedForms[key].push(questionObj);
        });
      }
    }
  });
  
  // Return processedForms, conceptUUIDs, and meta
  return {
    processedForms,
    conceptUUIDs,
    meta
  };
});
