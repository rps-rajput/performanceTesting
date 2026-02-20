const { execSync } = require("child_process");
const outputDir = "/Users/ravi/Desktop/jmeter/reports";

const urls = [
  "https://dne-front-test.daikinnortheast.com/",
  "https://dne-front-test.daikinnortheast.com/become-a-dealer",
  "https://dne-front-test.daikinnortheast.com/products-solutions/residential-hvac",
  "https://dne-front-test.daikinnortheast.com/news-resources",
  "https://dne-front-test.daikinnortheast.com/video-library",
  "https://dne-front-test.daikinnortheast.com/dealer-funds",
  "https://dne-front-test.daikinnortheast.com/subscribe",
  "https://dne-front-test.daikinnortheast.com/contact",
  "https://dne-front-test.daikinnortheast.com/trainings-events",
  "https://dne-front-test.daikinnortheast.com/rebates-offers",
  "https://dne-front-test.daikinnortheast.com/products-solutions/line-card",
  "https://dne-front-test.daikinnortheast.com/products-solutions/refrigeration",
  "https://dne-front-test.daikinnortheast.com/about",
  "https://dne-front-test.daikinnortheast.com/locations",
  "https://dne-front-test.daikinnortheast.com/products-solutions/aer",
  "https://dne-front-test.daikinnortheast.com/products-solutions/uep",
  "https://dne-front-test.daikinnortheast.com/sitefinity/anticsrf",
  "https://dne-front-test.daikinnortheast.com/forms/submit/sf_contact_us/en?sf_site=d3141ef2-47d8-40e0-b3ba-254532a2c66f&sf_site_temp=true",
  "https://dne-front-test.daikinnortheast.com/api/trainings-events-calendar/for-month-year?month=9&year=2025",
  "https://dne-front-test.daikinnortheast.com/api/trainings-events-calendar/for-month-year?month=10&year=2025",
  "https://maps.googleapis.com/maps/api/mapsjs/gen_204?csp_test=true",
  "https://maps.googleapis.com/$rpc/google.internal.maps.mapsjs.v1.MapsJsInternalService/GetViewportInfo"
];

urls.forEach((url, index) => {
  console.log(`\n🚀 Running Lighthouse (Desktop) for: ${url}\n`);
  try {
    const basePath = `${outputDir}/report-${index + 1}`;
    execSync(
      `lighthouse ${url} --output html --output json --output-path="${basePath}.json" --chrome-flags="--headless" --preset=desktop`,
      { stdio: "inherit" }
    );
    console.log(`✅ JSON Report saved: ${basePath}.json`);
  } catch (error) {
    console.error(`❌ Error running Lighthouse for ${url}`, error);
  }
});
