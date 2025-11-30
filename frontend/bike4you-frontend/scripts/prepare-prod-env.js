const fs = require('fs');

const auth = process.env.AUTH_API;
const inventory = process.env.INVENTORY_API;
const rental = process.env.RENTAL_API;

if (!auth || !inventory || !rental) {
  console.error("❌ Missing environment variables for prod build:");
  console.error("AUTH_API, INVENTORY_API, INVENTORY_API must be set");
  process.exit(1);
}

const content = `
export const environment = {
  production: true,
  authApi: '${auth}',
  inventoryApi: '${inventory}',
  rentalApi: '${rental}'
};
`;

fs.writeFileSync('./src/environments/environment.prod.ts', content);

console.log("✅ Generated environment.prod.ts for production build");
