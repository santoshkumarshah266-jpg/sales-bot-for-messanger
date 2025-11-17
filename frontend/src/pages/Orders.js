import { useState, useEffect } from 'react';
import axios from 'axios';
import { API } from '../App';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import { LayoutDashboard, Package, ShoppingBag, LogOut, Search } from 'lucide-react';

const Orders = ({ onLogout }) => {
  const navigate = useNavigate();
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');

  useEffect(() => {
    loadOrders();
  }, []);

  const loadOrders = async () => {
    try {
      const response = await axios.get(`${API}/admin/orders`);
      setOrders(response.data);
    } catch (error) {
      toast.error('Failed to load orders');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    onLogout();
    navigate('/login');
  };

  const updateOrderStatus = async (orderId, newStatus) => {
    try {
      await axios.put(`${API}/admin/orders/${orderId}/status`, { status: newStatus });
      toast.success('Order status updated');
      loadOrders();
    } catch (error) {
      toast.error('Failed to update order status');
    }
  };

  const filteredOrders = orders.filter(order => {
    const matchesSearch = 
      order.customer_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      order.phone.includes(searchTerm) ||
      order.order_id.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesStatus = filterStatus === 'all' || order.status === filterStatus;
    
    return matchesSearch && matchesStatus;
  });

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center">
      <div className="text-lg text-purple-600">Loading...</div>
    </div>;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-pink-50" data-testid="orders-page">
      {/* Header */}
      <header className="glass-effect border-b border-white/20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <h1 className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
              Nepal Fashion Store
            </h1>
            <button
              onClick={handleLogout}
              className="flex items-center gap-2 px-4 py-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
              data-testid="logout-button"
            >
              <LogOut className="w-4 h-4" />
              Logout
            </button>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            <button
              onClick={() => navigate('/')}
              className="flex items-center gap-2 px-4 py-4 text-gray-600 hover:text-purple-600 font-medium"
              data-testid="nav-dashboard"
            >
              <LayoutDashboard className="w-5 h-5" />
              Dashboard
            </button>
            <button
              onClick={() => navigate('/products')}
              className="flex items-center gap-2 px-4 py-4 text-gray-600 hover:text-purple-600 font-medium"
              data-testid="nav-products"
            >
              <Package className="w-5 h-5" />
              Products
            </button>
            <button
              onClick={() => navigate('/orders')}
              className="flex items-center gap-2 px-4 py-4 text-purple-600 border-b-2 border-purple-600 font-semibold"
              data-testid="nav-orders"
            >
              <ShoppingBag className="w-5 h-5" />
              Orders
            </button>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Orders Management</h2>

        {/* Filters */}
        <div className="glass-effect rounded-2xl p-6 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="relative">
              <Search className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search by name, phone, or order ID..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="input-field pl-10"
                data-testid="search-orders-input"
              />
            </div>
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="input-field"
              data-testid="filter-status-select"
            >
              <option value="all">All Status</option>
              <option value="pending">Pending</option>
              <option value="confirmed">Confirmed</option>
              <option value="shipped">Shipped</option>
              <option value="delivered">Delivered</option>
              <option value="cancelled">Cancelled</option>
            </select>
          </div>
        </div>

        {/* Orders List */}
        {filteredOrders.length === 0 ? (
          <div className="glass-effect rounded-2xl p-12 text-center">
            <ShoppingBag className="w-16 h-16 mx-auto mb-4 text-gray-400" />
            <h3 className="text-xl font-semibold text-gray-700 mb-2">No orders found</h3>
            <p className="text-gray-500">Orders will appear here once customers start purchasing</p>
          </div>
        ) : (
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Order ID</th>
                  <th>Customer</th>
                  <th>Phone</th>
                  <th>Items</th>
                  <th>Amount</th>
                  <th>Payment</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredOrders.map((order) => (
                  <tr key={order.order_id} data-testid="order-row">
                    <td className="font-mono text-sm">{order.order_id.substring(0, 8)}...</td>
                    <td className="font-semibold">{order.customer_name}</td>
                    <td>{order.phone}</td>
                    <td>{order.items?.length || 0} item(s)</td>
                    <td className="font-bold text-purple-600">Rs. {order.total_amount}</td>
                    <td>
                      <span className={`status-badge ${order.payment_method === 'COD' ? 'status-pending' : 'status-confirmed'}`}>
                        {order.payment_method}
                      </span>
                    </td>
                    <td>
                      <span className={`status-badge status-${order.status}`}>{order.status}</span>
                    </td>
                    <td>
                      <div className="flex gap-2">
                        {order.status === 'pending' && (
                          <button
                            onClick={() => updateOrderStatus(order.order_id, 'confirmed')}
                            className="px-3 py-1 bg-blue-50 text-blue-600 rounded hover:bg-blue-100 text-sm font-semibold"
                            data-testid="confirm-order-button"
                          >
                            Confirm
                          </button>
                        )}
                        {order.status === 'confirmed' && (
                          <button
                            onClick={() => updateOrderStatus(order.order_id, 'shipped')}
                            className="px-3 py-1 bg-purple-50 text-purple-600 rounded hover:bg-purple-100 text-sm font-semibold"
                            data-testid="ship-order-button"
                          >
                            Ship
                          </button>
                        )}
                        {order.status === 'shipped' && (
                          <button
                            onClick={() => updateOrderStatus(order.order_id, 'delivered')}
                            className="px-3 py-1 bg-green-50 text-green-600 rounded hover:bg-green-100 text-sm font-semibold"
                            data-testid="deliver-order-button"
                          >
                            Deliver
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </main>
    </div>
  );
};

export default Orders;