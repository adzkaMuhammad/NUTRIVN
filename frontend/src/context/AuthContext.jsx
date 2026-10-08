import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { toast } from "sonner";
import { supabase, authEnabled, getDevToken } from "@/lib/supabase";
import { getMe, addFavorite, removeFavorite } from "@/lib/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [stats, setStats] = useState(null);
  const [favorites, setFavorites] = useState([]);
  const [loading, setLoading] = useState(true);

  const loadMe = useCallback(async () => {
    try {
      const me = await getMe();
      setUser(me.user);
      setStats(me.stats);
      setFavorites(me.favorites);
    } catch (e) {
      setUser(null);
      setStats(null);
      setFavorites([]);
      if (!supabase) localStorage.removeItem("nv_dev_token");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (!supabase) {
      if (getDevToken()) loadMe(); else setLoading(false);
      return;
    }
    supabase.auth.getSession().then(({ data }) => {
      if (data.session) loadMe(); else setLoading(false);
    });
    const { data: sub } = supabase.auth.onAuthStateChange((_event, session) => {
      if (session) loadMe();
      else { setUser(null); setStats(null); setFavorites([]); setLoading(false); }
    });
    return () => sub.subscription.unsubscribe();
  }, [loadMe]);

  const signInWithGoogle = useCallback(async () => {
    if (!supabase) { toast.error("Login Google belum dikonfigurasi (REACT_APP_SUPABASE_URL)."); return; }
    const { error } = await supabase.auth.signInWithOAuth({
      provider: "google",
      options: { redirectTo: `${window.location.origin}/auth/callback` },
    });
    if (error) toast.error(error.message);
  }, []);

  const signOut = useCallback(async () => {
    if (supabase) await supabase.auth.signOut();
    localStorage.removeItem("nv_dev_token");
    setUser(null); setStats(null); setFavorites([]);
  }, []);

  const toggleFavorite = useCallback(async (slug) => {
    const isFav = favorites.includes(slug);
    setFavorites((f) => (isFav ? f.filter((s) => s !== slug) : [slug, ...f]));
    try {
      const res = isFav ? await removeFavorite(slug) : await addFavorite(slug);
      setFavorites(res.favorites);
      toast.success(isFav ? "Dihapus dari favorit" : "Disimpan ke favorit");
    } catch (e) {
      setFavorites((f) => (isFav ? [slug, ...f] : f.filter((s) => s !== slug)));
      toast.error("Gagal menyimpan favorit");
    }
  }, [favorites]);

  const value = useMemo(() => ({
    user, stats, favorites, loading, authEnabled,
    isFavorite: (slug) => favorites.includes(slug),
    toggleFavorite, signInWithGoogle, signOut, refresh: loadMe, setStats,
  }), [user, stats, favorites, loading, toggleFavorite, signInWithGoogle, signOut, loadMe]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export const useAuth = () => useContext(AuthContext);
