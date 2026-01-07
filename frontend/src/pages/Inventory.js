import React, { useState } from 'react';

const Inventory = () => {
  // eslint-disable-next-line no-unused-vars
  const [products, setProducts] = useState([
    { id: 1, name: 'PVC Pipe 1/2 inch', category: 'Plumbing', stock: 50, price: 10.99, sku: 'PVC001' },
    { id: 2, name: 'Switch', category: 'Electronics', stock: 20, price: 5.50, sku: 'SWT001' },
  ]);

  const [search, setSearch] = useState('');

  const filteredProducts = products.filter(product =>
    product.name.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div>
      <h2>Inventory Management</h2>
      <input
        type="text"
        placeholder="Search products..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
      />
      <table border="1" style={{ width: '100%', marginTop: '20px' }}>
        <thead>
          <tr>
            <th>Name</th>
            <th>Category</th>
            <th>Stock</th>
            <th>Price</th>
            <th>SKU</th>
          </tr>
        </thead>
        <tbody>
          {filteredProducts.map(product => (
            <tr key={product.id} style={product.stock < 10 ? { backgroundColor: 'red' } : {}}>
              <td>{product.name}</td>
              <td>{product.category}</td>
              <td>{product.stock}</td>
              <td>${product.price}</td>
              <td>{product.sku}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <button>Add Product</button>
    </div>
  );
};

export default Inventory;