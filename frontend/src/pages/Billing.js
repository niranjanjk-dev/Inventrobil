import React, { useState } from 'react';

const Billing = () => {
  const [cart, setCart] = useState([]);
  const [search, setSearch] = useState('');

  // Mock products
  const products = [
    { id: 1, name: 'PVC Pipe 1/2 inch', price: 10.99 },
    { id: 2, name: 'Switch', price: 5.50 },
  ];

  const addToCart = (product) => {
    setCart([...cart, product]);
  };

  const total = cart.reduce((sum, item) => sum + item.price, 0);

  return (
    <div style={{ display: 'flex' }}>
      <div style={{ width: '50%', padding: '20px' }}>
        <h3>Product Search</h3>
        <input
          type="text"
          placeholder="Search products..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <ul>
          {products.filter(p => p.name.toLowerCase().includes(search.toLowerCase())).map(product => (
            <li key={product.id}>
              {product.name} - ${product.price}
              <button onClick={() => addToCart(product)}>Add to Cart</button>
            </li>
          ))}
        </ul>
      </div>
      <div style={{ width: '50%', padding: '20px' }}>
        <h3>Current Bill</h3>
        <ul>
          {cart.map((item, index) => (
            <li key={index}>{item.name} - ${item.price}</li>
          ))}
        </ul>
        <p>Total: ${total.toFixed(2)}</p>
        <button>Checkout</button>
      </div>
    </div>
  );
};

export default Billing;