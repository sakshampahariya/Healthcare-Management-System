import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import { ProtectedRoute } from "./components/layout/ProtectedRoute";
import { MainLayout } from "./components/layout/MainLayout";
import { Login } from "./pages/Login";
import { Signup } from "./pages/Signup";
import { Dashboard } from "./pages/Dashboard";
import { DiagnosticCentres } from "./pages/DiagnosticCentres";
import { CentreDetails } from "./pages/CentreDetails";
import { Tests } from "./pages/Tests";
import { MyBookings } from "./pages/MyBookings";
import { BookingDetails } from "./pages/BookingDetails";
import { SimulatedPayment } from "./pages/SimulatedPayment";
import { Profile } from "./pages/Profile";

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          {/* Public Authentication Routes */}
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />

          {/* Protected Application Routes */}
          <Route element={<ProtectedRoute />}>
            <Route element={<MainLayout />}>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/centres" element={<DiagnosticCentres />} />
              <Route path="/centres/:id" element={<CentreDetails />} />
              <Route path="/tests" element={<Tests />} />
              <Route path="/bookings" element={<MyBookings />} />
              <Route path="/bookings/:id" element={<BookingDetails />} />
              <Route path="/payment/:bookingId" element={<SimulatedPayment />} />
              <Route path="/profile" element={<Profile />} />
            </Route>
          </Route>

          {/* Fallback Route */}
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
};

export default App;
