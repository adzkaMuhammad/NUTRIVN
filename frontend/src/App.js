import "@/App.css";
import { BrowserRouter, Routes, Route, Navigate, useLocation } from "react-router-dom";
import { Toaster } from "@/components/ui/sonner";
import { AuthProvider, useAuth } from "@/context/AuthContext";
import HomePage from "@/pages/HomePage";
import ScanPage from "@/pages/ScanPage";
import RecipesPage from "@/pages/RecipesPage";
import RecipeDetailPage from "@/pages/RecipeDetailPage";
import MoodPage from "@/pages/MoodPage";
import LoginPage from "@/pages/LoginPage";
import AuthCallbackPage from "@/pages/AuthCallbackPage";
import ProfilePage from "@/pages/ProfilePage";

function Welcome({ children }) {
  const { user, loading } = useAuth();
  const { pathname } = useLocation();
  if (loading) return null;
  if (!user && !localStorage.getItem("nv_welcomed") && pathname === "/") return <Navigate to="/login" replace />;
  return children;
}

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/auth/callback" element={<AuthCallbackPage />} />
          <Route path="/" element={<Welcome><HomePage /></Welcome>} />
          <Route path="/scan" element={<ScanPage />} />
          <Route path="/recipes" element={<RecipesPage />} />
          <Route path="/recipes/:slug" element={<RecipeDetailPage />} />
          <Route path="/mood" element={<MoodPage />} />
          <Route path="/profile" element={<ProfilePage />} />
        </Routes>
      </BrowserRouter>
      <Toaster position="top-center" richColors />
    </AuthProvider>
  );
}

export default App;
