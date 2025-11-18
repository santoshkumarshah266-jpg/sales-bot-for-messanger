import { useState, useEffect } from 'react';
import axios from 'axios';
import { API } from '../App';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import { LayoutDashboard, Package, ShoppingBag, LogOut, TrendingUp, Calendar, DollarSign } from 'lucide-react';

const Dashboard = ({ onLogout }) => {
  const navigate = useNavigate();
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    try {
      const response = await axios.get(`${API}/admin/analytics`);
      setAnalytics(response.data);
    } catch (error) {
      toast.error('Failed to load analytics');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    onLogout();
    navigate('/login');
  };

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center">
      <div className="text-lg text-purple-600">Loading...</div>
    </div>;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-pink-50" data-testid="dashboard-page">
      {/* Header */}
      <header className="glass-effect border-b border-white/20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <h1 className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
              Urban Fashion
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
              className="flex items-center gap-2 px-4 py-4 text-purple-600 border-b-2 border-purple-600 font-semibold"
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
              className="flex items-center gap-2 px-4 py-4 text-gray-600 hover:text-purple-600 font-medium"
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
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="stat-card" data-testid="stat-today">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-gray-600 font-semibold">Today</h3>
              <Calendar className="w-6 h-6 text-purple-600" />
            </div>
            <div className="space-y-2">
              <p className="text-3xl font-bold text-gray-900">{analytics?.today?.orders || 0}</p>
              <p className="text-sm text-gray-500">Orders</p>
              <div className="flex items-center gap-2 mt-3 pt-3 border-t border-gray-100">
                <DollarSign className="w-5 h-5 text-green-600" />
                <span className="text-xl font-bold text-green-600">Rs. {analytics?.today?.revenue || 0}</span>
              </div>
            </div>
          </div>

          <div className="stat-card" data-testid="stat-week">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-gray-600 font-semibold">This Week</h3>
              <TrendingUp className="w-6 h-6 text-blue-600" />
            </div>
            <div className="space-y-2">
              <p className="text-3xl font-bold text-gray-900">{analytics?.week?.orders || 0}</p>
              <p className="text-sm text-gray-500">Orders</p>
              <div className="flex items-center gap-2 mt-3 pt-3 border-t border-gray-100">
                <DollarSign className="w-5 h-5 text-green-600" />
                <span className="text-xl font-bold text-green-600">Rs. {analytics?.week?.revenue || 0}</span>
              </div>
            </div>
          </div>

          <div className="stat-card" data-testid="stat-month">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-gray-600 font-semibold">This Month</h3>
              <ShoppingBag className="w-6 h-6 text-pink-600" />
            </div>
            <div className="space-y-2">
              <p className="text-3xl font-bold text-gray-900">{analytics?.month?.orders || 0}</p>
              <p className="text-sm text-gray-500">Orders</p>
              <div className="flex items-center gap-2 mt-3 pt-3 border-t border-gray-100">
                <DollarSign className="w-5 h-5 text-green-600" />
                <span className="text-xl font-bold text-green-600">Rs. {analytics?.month?.revenue || 0}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Recent Orders */}
        <div className="glass-effect rounded-2xl p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Recent Orders</h2>
          {analytics?.recent_orders && analytics.recent_orders.length > 0 ? (
            <div className="space-y-3">
              {analytics.recent_orders.map((order) => (
                <div key={order.order_id} className="flex items-center justify-between p-4 bg-white rounded-lg hover:shadow-md transition-shadow" data-testid="recent-order">
                  <div>
                    <p className="font-semibold text-gray-900">{order.customer_name}</p>
                    <p className="text-sm text-gray-600">{order.phone}</p>
                  </div>
                  <div className="text-right">
                    <p className="font-bold text-purple-600">Rs. {order.total_amount}</p>
                    <span className={`status-badge status-${order.status}`}>{order.status}</span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-center text-gray-500 py-8">No orders yet</p>
          )}
        </div>

        {/* Quick Actions */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
          <button
            onClick={() => navigate('/products')}
            className="p-6 bg-gradient-to-br from-purple-600 to-blue-600 text-white rounded-2xl hover:shadow-xl transition-all transform hover:scale-105"
            data-testid="quick-action-products"
          >
            <Package className="w-8 h-8 mb-3" />
            <h3 className="text-xl font-bold mb-2">Manage Products</h3>
            <p className="text-purple-100">Add, edit, or remove products from your catalog</p>
          </button>

          <button
            onClick={() => navigate('/orders')}
            className="p-6 bg-gradient-to-br from-pink-600 to-orange-600 text-white rounded-2xl hover:shadow-xl transition-all transform hover:scale-105"
            data-testid="quick-action-orders"
          >
            <ShoppingBag className="w-8 h-8 mb-3" />
            <h3 className="text-xl font-bold mb-2">View All Orders</h3>
            <p className="text-pink-100">Track and manage customer orders</p>
          </button>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;