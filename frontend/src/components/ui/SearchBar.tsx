import { Search, X } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { useDebounce } from "../../hooks/useDebounce";
import { DEBOUNCE_DELAY } from "../../utils/constants";

interface SearchBarProps {
  placeholder?: string;
  onSearch: (value: string) => void;
  initialValue?: string;
}

export function SearchBar({
  placeholder = "Buscar...",
  onSearch,
  initialValue = "",
}: Readonly<SearchBarProps>) {
  const [value, setValue] = useState(initialValue);
  const [focused, setFocused] = useState(false);
  const debounced = useDebounce(value, DEBOUNCE_DELAY);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    onSearch(debounced);
  }, [debounced, onSearch]);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "/" && document.activeElement?.tagName !== "INPUT") {
        e.preventDefault();
        inputRef.current?.focus();
      }
      if (e.key === "Escape" && focused) {
        inputRef.current?.blur();
      }
    };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [focused]);

  return (
    <div
      className="relative transition-all duration-200"
      style={{
        filter: focused ? "drop-shadow(0 0 8px color-mix(in srgb, var(--color-accent) 25%, transparent))" : "none",
      }}
    >
      <Search
        size={16}
        className="absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none transition-colors duration-200"
        style={{ color: focused ? "var(--color-accent)" : "var(--color-text-muted)" }}
      />

      <input
        ref={inputRef}
        type="text"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onFocus={() => setFocused(true)}
        onBlur={() => setFocused(false)}
        placeholder={placeholder}
        className="w-full rounded-xl border py-2.5 pl-10 pr-16 text-sm transition-all duration-200 focus:outline-none"
        style={{
          background: "var(--color-bg-elevated)",
          borderColor: focused ? "var(--color-accent)" : "var(--color-border)",
          color: "var(--color-text-primary)",
        }}
      />

      <div className="absolute right-2.5 top-1/2 -translate-y-1/2 flex items-center gap-1.5">
        {value ? (
          <button
            onClick={() => { setValue(""); inputRef.current?.focus(); }}
            className="rounded-md p-0.5 transition-colors hover:text-rose-400"
            style={{ color: "var(--color-text-muted)" }}
            type="button"
          >
            <X size={14} />
          </button>
        ) : !focused && (
          <kbd
            className="hidden sm:inline-flex items-center rounded px-1.5 py-0.5 text-[10px] font-medium leading-none select-none"
            style={{
              background: "var(--color-bg-base)",
              border: "1px solid var(--color-border)",
              color: "var(--color-text-muted)",
            }}
          >
            /
          </kbd>
        )}
      </div>
    </div>
  );
}
