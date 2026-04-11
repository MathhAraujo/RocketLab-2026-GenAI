import { useEffect, useState } from "react";
import { DEBOUNCE_DELAY } from "../utils/constants";

export function useDebounce<T>(value: T, delay = DEBOUNCE_DELAY): T {
  const [debounced, setDebounced] = useState<T>(value);

  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);

  return debounced;
}
