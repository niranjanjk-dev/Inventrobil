import React, { createContext, useState, useCallback, useEffect } from 'react';

const InventoryContext = createContext();

// Initialize with sample data
const INITIAL_PRODUCTS = [
  { id: 1, name: 'PVC Pipe 1/2 inch', category: 'Plumbing', stock: 50, price: 10.99, sku: 'PVC001' },
  { id: 2, name: 'Copper Wire 2.5mm', category: 'Electronics', stock: 5, price: 15.50, sku: 'COP001' },
  { id: 3, name: 'Switch Socket', category: 'Electronics', stock: 20, price: 5.50, sku: 'SWT001' },
  { id: 4, name: 'PVC Pipe 1 inch', category: 'Plumbing', stock: 35, price: 18.99, sku: 'PVC002' },
  { id: 5, name: 'Electrical Box', category: 'Electronics', stock: 8, price: 8.75, sku: 'ELB001' },
];

const STORAGE_KEY = 'inventrobil_inventory';
const BILLING_KEY = 'inventrobil_billing';

export const InventoryProvider = ({ children }) => {
  const [products, setProducts] = useState([]);
  const [billingHistory, setBillingHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  // Load data from localStorage on mount
  useEffect(() => {
    const loadData = () => {
      try {
        const storedProducts = localStorage.getItem(STORAGE_KEY);
        const storedBilling = localStorage.getItem(BILLING_KEY);

        if (storedProducts) {
          setProducts(JSON.parse(storedProducts));
        } else {
          setProducts(INITIAL_PRODUCTS);
          localStorage.setItem(STORAGE_KEY, JSON.stringify(INITIAL_PRODUCTS));
        }

        if (storedBilling) {
          setBillingHistory(JSON.parse(storedBilling));
        }
      } catch (error) {
        console.error('Error loading data from localStorage:', error);
        setProducts(INITIAL_PRODUCTS);
      } finally {
        setIsLoading(false);
      }
    };

    loadData();
  }, []);

  // Persist products to localStorage whenever they change
  useEffect(() => {
    if (!isLoading && products.length > 0) {
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(products));
      } catch (error) {
        console.error('Error saving products to localStorage:', error);
      }
    }
  }, [products, isLoading]);

  // Persist billing history to localStorage whenever it changes
  useEffect(() => {
    if (!isLoading) {
      try {
        localStorage.setItem(BILLING_KEY, JSON.stringify(billingHistory));
      } catch (error) {
        console.error('Error saving billing history to localStorage:', error);
      }
    }
  }, [billingHistory, isLoading]);

  // Add a new product
  const addProduct = useCallback((product) => {
    setProducts((prevProducts) => {
      const newProduct = {
        id: Math.max(...prevProducts.map((p) => p.id), 0) + 1,
        ...product,
        stock: parseInt(product.stock),
        price: parseFloat(product.price),
      };
      return [...prevProducts, newProduct];
    });
  }, []);

  // Update an existing product
  const updateProduct = useCallback((id, updatedProduct) => {
    setProducts((prevProducts) =>
      prevProducts.map((product) =>
        product.id === id
          ? {
              ...product,
              ...updatedProduct,
              stock: parseInt(updatedProduct.stock || product.stock),
              price: parseFloat(updatedProduct.price || product.price),
            }
          : product
      )
    );
  }, []);

  // Delete a product
  const deleteProduct = useCallback((id) => {
    setProducts((prevProducts) => prevProducts.filter((product) => product.id !== id));
  }, []);

  // Update stock (used when billing)
  const updateStock = useCallback((id, newStock) => {
    setProducts((prevProducts) =>
      prevProducts.map((product) =>
        product.id === id ? { ...product, stock: Math.max(0, newStock) } : product
      )
    );
  }, []);

  // Add billing record
  const addBillingRecord = useCallback((record) => {
    setBillingHistory((prevHistory) => [
      {
        id: Date.now(),
        timestamp: new Date().toISOString(),
        ...record,
      },
      ...prevHistory,
    ]);
  }, []);

  // Export inventory as JSON
  const exportInventory = useCallback(() => {
    const data = {
      exportDate: new Date().toISOString(),
      totalProducts: products.length,
      products: products,
    };
    return data;
  }, [products]);

  // Import inventory from JSON
  const importInventory = useCallback((data) => {
    if (!data.products || !Array.isArray(data.products)) {
      throw new Error('Invalid inventory data format');
    }
    setProducts(data.products);
  }, []);

  // Get product by ID
  const getProduct = useCallback(
    (id) => products.find((product) => product.id === id),
    [products]
  );

  // Get all products
  const getAllProducts = useCallback(() => products, [products]);

  // Get billing history
  const getBillingHistory = useCallback(() => billingHistory, [billingHistory]);

  const value = {
    // State
    products,
    billingHistory,
    isLoading,

    // Product operations
    addProduct,
    updateProduct,
    deleteProduct,
    updateStock,
    getProduct,
    getAllProducts,

    // Billing operations
    addBillingRecord,
    getBillingHistory,

    // Import/Export
    exportInventory,
    importInventory,
  };

  return (
    <InventoryContext.Provider value={value}>
      {children}
    </InventoryContext.Provider>
  );
};

export const useInventory = () => {
  const context = React.useContext(InventoryContext);
  if (!context) {
    throw new Error('useInventory must be used within an InventoryProvider');
  }
  return context;
};
