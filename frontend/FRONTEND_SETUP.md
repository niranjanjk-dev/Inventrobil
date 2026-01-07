# Inventrobil Web - Frontend Base Codebase

## Project Overview
This is the **Frontend** foundation for the Inventrobil Web - an Inventory and Billing Management System designed for shop owners and staff to manage inventory, process billing, and track financial performance.

## Current Structure

```
frontend/
├── public/
│   ├── index.html
│   └── favicon.ico
├── src/
│   ├── components/
│   │   └── Header.js         (Navigation header with links)
│   ├── pages/
│   │   ├── Home.js           (Dashboard/home page)
│   │   ├── Inventory.js      (Inventory management page with search & low-stock alerts)
│   │   └── Billing.js        (POS/Billing page with cart and calculations)
│   ├── App.js                (Main app with routing)
│   ├── App.css               (Styling)
│   └── index.js              (React entry point)
├── package.json
└── README.md
```

## Features Implemented (Phase 1)

### ✅ Basic Pages
- **Home Page**: Welcome/dashboard view
- **Inventory Page**: 
  - Table display of products with Name, Category, Stock, Price, SKU
  - Search functionality to filter products
  - Low stock alert (red highlighting for stock < 10)
  - Add Product button (placeholder)
- **Billing Page**:
  - Split-screen layout (Product Search | Cart)
  - Product search and add-to-cart functionality
  - Real-time bill total calculation

### ✅ Navigation
- Header with links to all main pages
- React Router for client-side routing

### ✅ Responsive Design
- Basic styling structure ready for enhancement

## Getting Started

### Prerequisites
- Node.js (v14+)
- npm or yarn

### Installation & Running

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start development server**
   ```bash
   npm start
   ```

4. **Open in browser**
   The app will automatically open at `http://localhost:3000`

## What's Included

- ✅ React 18 with React Router v6
- ✅ Basic component structure (Header, Pages)
- ✅ Mock data for products
- ✅ Basic search and filtering
- ✅ Cart functionality with totals
- ✅ Low stock alerts

## Future Enhancements

### Phase 2: API Integration
- [ ] Connect to backend API endpoints
- [ ] Real product data from database
- [ ] User authentication (login/logout)
- [ ] Role-based access (Admin/Staff)

### Phase 3: Features
- [ ] Advanced filtering and sorting
- [ ] Edit/Delete products (admin only)
- [ ] Product image display with auto-fetch fallback
- [ ] Invoice PDF generation
- [ ] Discount and tax calculations
- [ ] Financial reports and analytics

### Phase 4: UI/UX Improvements
- [ ] CSS framework (Bootstrap, Tailwind, or Material-UI)
- [ ] Form validation
- [ ] Error handling and notifications
- [ ] Loading states
- [ ] Responsive mobile design

### Phase 5: Deployment
- [ ] Build optimization
- [ ] Hosting setup
- [ ] Environment configuration

## Tech Stack

- **Framework**: React 18
- **Routing**: React Router v6
- **Language**: JavaScript (ES6+)
- **Styling**: CSS (to be enhanced)
- **Build Tool**: Create React App

## File Structure Explanation

- `Header.js`: Main navigation component with links
- `Home.js`: Landing/dashboard page
- `Inventory.js`: Inventory management with search and display
- `Billing.js`: Point of Sale (POS) interface with cart
- `App.js`: Main app component with routing configuration

## Notes

- Mock data is hardcoded for now and will be replaced with API calls
- Styling is minimal; use a CSS framework in the next phase
- All calculations are client-side for now

---

**Status**: Base Frontend Ready
**Next Step**: Backend API implementation, then integration
