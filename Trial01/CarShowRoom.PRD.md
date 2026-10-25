# 🚗 Product Requirement Document (PRD)
**Project:** Car Sales & Booking Backend  
**Scope:** Backend API endpoints and logic for handling user authentication, catalog browsing, car customization, cart management, and booking flow.

---

## 1. Login
**Endpoint:** `POST /login`  
**Request:**
```json
{
  "username": "string",
  "password": "string"
}
Response:

json
{
  "success": true,
  "salesRepName": "string"
}
2. Fetch Catalog
Endpoint: GET /catalog  
Request:  
No parameters.
Response:

json
{
  "cars": [
    {
      "carId": "string",
      "model": "string",
      "price": "number",
      "specs": { "engine": "string", "color": "string" }
    }
  ]
}
3. Fetch Car Detail
Endpoint: GET /cardetail/{carId}  
Request:  
Path parameter: carId  
Response:

json
{
  "carId": "string",
  "details": {
    "engineOptions": {
      "default": "string",
      "selected": "string"
    },
    "units": [
      { "name": "string", "value": "string" }
    ]
  }
}
4. Add to Cart
Endpoint: POST /cart  
Request:

json
{
  "customerId": "string",
  "piInfo": {
    "carId": "string",
    "customizations": { "engine": "string", "color": "string" }
  }
}
Response:

json
{
  "cartId": "string"
}
5. Trigger Booking
Endpoint: POST /booking  
Request:

json
{
  "customerId": "string",
  "carId": "string"
}
Response:

json
{
  "bookingId": "string"
}
6. Fetch Custom Info
Endpoint: GET /custominfo  
Request:

json
{
  "piInfo": "string"
}
Response:

json
{
  "cartInfo": { "carId": "string", "details": "object" },
  "orderInfo": { "bookingId": "string", "status": "string" }
}
7. Fetch Cart Info
Endpoint: GET /cart/{cartId}  
Request:  
Path parameter: cartId  
Response:

json
{
  "cartId": "string",
  "items": [
    {
      "carId": "string",
      "customizations": { "engine": "string", "color": "string" },
      "price": "number"
    }
  ]
}
8. Fetch Order Info
Endpoint: GET /order/{bookingId}  
Request:  
Path parameter: bookingId  
Response:

json
{
  "bookingId": "string",
  "carId": "string",
  "customerId": "string",
  "status": "string",
  "confirmationDate": "string"
}
🔒 Security & Compliance
All endpoints must use HTTPS.

Authentication via tokens (JWT or OAuth).

Input validation to prevent SQL injection.

📊 Database Requirements
MySQL backend.

Tables: Users, Cars, CustomizationOptions, Cart, Orders.

Relationships:

Users ↔ Cart ↔ Orders

Cars ↔ CustomizationOptions