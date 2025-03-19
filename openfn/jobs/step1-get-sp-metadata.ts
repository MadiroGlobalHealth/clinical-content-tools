cursor($.lastSync, { defaultValue: 'now', key: 'syncedAt' });
cursor('now', { key: 'lastSync' });

fn(state => {
  state.siteName = 'GRP-GVA-LIME Project';
  state.sheets = ['OptionSets', 'identifiers', 'Places of living'];
  state.folderPath = '/General/Phase II/Metadata/Shared/ready-for-test';
  return state;
});

get('sites', { search: $.siteName }).then(state => {
  const site = state.data.value.find(i => i.displayName === state.siteName);
  if (!site) {
    throw new Error(`Could not find sharepoint site: ${state.siteName}`);
  }
  state.siteId = site.id;

  return state;
});

getDrive({ id: $.siteId, owner: 'sites' });

getFolder($.folderPath);

fn(state => {
  let targetFile;

  // Filter for .xlsx files only
  const xlsxFiles = state.data.value.filter(file =>
    file.name.toLowerCase().endsWith('.xlsx')
  );

  if (xlsxFiles.length === 0) {
    throw new Error('No Excel (.xlsx) files found in the specified folder.');
  }

  if (state.fileName) {
    // If a specific fileName is provided, find that file among the xlsx files
    targetFile = xlsxFiles.find(file => file.name === state.fileName);

    if (!targetFile) {
      console.log(
        `Excel file "${state.fileName}" not found. Falling back to most recent Excel file.`
      );
    }
  }

  if (!targetFile) {
    // If no fileName was provided or the specified file wasn't found,
    // sort the xlsx files by the date extracted from the filename and get the most recent
    const sortedFiles = xlsxFiles.sort((a, b) => {
      const dateA = a.lastModifiedDateTime;
      const dateB = b.lastModifiedDateTime;
      if (dateA && dateB) {
        return dateB - dateA; // Sort in descending order (most recent first)
      }
      return 0; // If dates can't be extracted, maintain original order
    });
    targetFile = sortedFiles[0];
  }

  if (!targetFile) {
    throw new Error('No suitable Excel file found in the specified folder.');
  }

  console.log('Target Excel file:', targetFile.name);
  console.log('File date:', targetFile.lastModifiedDateTime);

  // Store the target file information in state for further use
  state.targetFile = targetFile;

  // Construct the workbookBase URL
  state.workbookBase = `sites/${state.siteId}/drives/${state.drives.default.id}/items/${targetFile.id}/workbook`;

  return state;
});

get(`${$.workbookBase}/worksheets('omrs-form-metadata')/usedRange`).then(
  state => {
    const [headers, ...rows] = state.data.values;
    state.formMetadata = rows
      .map(row =>
        row.reduce((obj, value, index) => {
          if (value) {
            obj[headers[index]] = value;
          }
          return obj;
        }, {})
      )
      .filter(obj => Object.keys(obj).length > 0 && obj['Active']);

    state.sheets.push(
      ...state.formMetadata.map(obj => obj['OMRS form sheet name'])
    );
    return state;
  }
);

each(
  $.sheets,
  get(`${$.workbookBase}/worksheets('${$.data}')/usedRange`).then(state => {
    const sheetName = state.references.at(-1);
    console.log('Fetched sheet: ', sheetName);
    state[sheetName] = state.data.values;
    return state;
  })
);

fn(state => {
  delete state.data;
  delete state.response;
  delete state.references;
  return state;
});
