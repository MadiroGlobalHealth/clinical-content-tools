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
        found: state.statistics.concepts.emrFound,
        notFound: state.statistics.concepts.emrNotFound
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
