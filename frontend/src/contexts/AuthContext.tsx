import {
  createContext,
  useCallback,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { login as apiLogin } from "../api/auth";
import type { AuthUser, LoginRequest } from "../types/auth";
import { AUTH_STORAGE_KEYS } from "../utils/constants";

interface AuthContextValue {
  user: AuthUser | null;
  token: string | null;
  isLoading: boolean;
  login: (data: LoginRequest) => Promise<void>;
  logout: () => void;
}

export const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: Readonly<{ children: ReactNode }>) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [token, setToken] = useState<string | null>(
    () => localStorage.getItem(AUTH_STORAGE_KEYS.token)
  );
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const stored = localStorage.getItem(AUTH_STORAGE_KEYS.token);
    const storedUser = localStorage.getItem(AUTH_STORAGE_KEYS.user);
    if (stored && storedUser) {
      setToken(stored);
      setUser(JSON.parse(storedUser) as AuthUser);
    }
    setIsLoading(false);
  }, []);

  const login = useCallback(async (data: LoginRequest) => {
    const response = await apiLogin(data);
    const authUser: AuthUser = { username: data.username };
    localStorage.setItem(AUTH_STORAGE_KEYS.token, response.access_token);
    localStorage.setItem(AUTH_STORAGE_KEYS.user, JSON.stringify(authUser));
    setToken(response.access_token);
    setUser(authUser);
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem(AUTH_STORAGE_KEYS.token);
    localStorage.removeItem(AUTH_STORAGE_KEYS.user);
    setToken(null);
    setUser(null);
  }, []);

  const value = useMemo(() => ({ user, token, isLoading, login, logout }), [user, token, isLoading, login, logout]);

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}
