fn(state => {
    const { reports } = state;
    const mergedMeta = {};
    const missingExternalIds = {};
    const stats = {};
    
    const mergedReport = Object.entries(reports).reduce((acc, [source, report]) => {
      // Store the timestamp for each source
      mergedMeta[source] = report.meta.timestamp;
      
      // Initialize missing externalIds and stats for this source
      missingExternalIds[source] = [];
      stats[source] = {
        totalForms: 0,
        formsCounted: 0,
        missingExternalIds: 0
      };
  
      Object.entries(report.processedForms).forEach(([formName, forms]) => {
        stats[source].totalForms += forms.length;
        
        forms.forEach(form => {
          const existingForm = acc.find(f => 
            f.externalId.value === form.externalId.value && 
            f.formName === formName
          );
          if (existingForm) {
            existingForm.externalId[source] = form.externalId[source] || 'Missing';
            if (form.externalId[source] === undefined) {
              missingExternalIds[source].push(form.externalId.value);
              stats[source].missingExternalIds++;
            } else {
              stats[source].formsCounted++;
            }
          } else {
            acc.push({
              ...form,
              formName,
              externalId: {
                ...form.externalId,
                [source]: form.externalId[source] || 'Missing'
              }
            });
            if (form.externalId[source] === undefined) {
              missingExternalIds[source].push(form.externalId.value);
              stats[source].missingExternalIds++;
            } else {
              stats[source].formsCounted++;
            }
          }
        });
      });
      return acc;
    }, []);
  
    return { 
      mergedReport,
      mergedMeta,
      missingExternalIds,
      stats
    };
  });