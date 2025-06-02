cursor($.lastSync, { defaultValue: 'now', key: 'syncedAt' });
cursor('now', { key: 'lastSync' });

fn(state => {
  state.siteName = 'GRP-GVA-LIME Project';
  state.sheets = ['OptionSets', 'identifiers', 'Places of living'];
  state.folderPath = '/General/Phase II/Iraq/Metadata';
  state.fileName = 'LIME EMR - Iraq Metadata - Release 1.xlsx';
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
  const targetFile = state.data.value.find(file => file.name === state.fileName);

  if (!targetFile) {
    throw new Error(`File "${state.fileName}" not found in the specified folder.`);
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
      .filter(obj => Object.keys(obj).length > 0 && obj['Testing']);

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
