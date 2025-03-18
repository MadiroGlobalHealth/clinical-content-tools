// Send progress on Identifiers with OpenMRS
post(
  'https://concept-flow-alpha.vercel.app/api/updateStatus',
  {
    body: {
      system: "OpenMRS",
      group: "identifiers",
      message: "Verification Progress",
      stats: {
        total: state.identifiers.length,
        notChecked: state.statistics.identifiers.notChecked,
        found: state.statistics.identifiers.found,
        notFound: state.statistics.identifiers.notFound
      },
      meta: {
        validationUrl: "http://lime-mosul-uat.madiro.org"
      }
    },
    headers: {
      'Content-Type': 'application/json'
    }
  }
);

// Send progress on Attributes with OpenMRS
post(
  'https://concept-flow-alpha.vercel.app/api/updateStatus',
  {
    body: {
      system: "OpenMRS",
      group: "personattributetypes",
      message: "Verification Progress",
      stats: {
        total: state.attributes.length,
        notChecked: state.statistics.personattributetypes.notChecked,
        found: state.statistics.personattributetypes.found,
        notFound: state.statistics.personattributetypes.notFound
      },
      meta: {
        validationUrl: "http://lime-mosul-uat.madiro.org"
      }
    },
    headers: {
      'Content-Type': 'application/json'
    }
  }
);

// Send progress on Concepts with OpenMRS
post(
  'https://concept-flow-alpha.vercel.app/api/updateStatus',
  {
    body: {
      system: "OpenMRS",
      group: "concepts",
      message: "Verification Progress",
      stats: {
        total: state.concepts.length,
        notChecked: state.statistics.concepts.notChecked,
        found: state.statistics.concepts.found,
        notFound: state.statistics.concepts.notFound
      },
      meta: {
        validationUrl: "http://lime-mosul-uat.madiro.org"
      }
    },
    headers: {
      'Content-Type': 'application/json'
    }
  }
);
