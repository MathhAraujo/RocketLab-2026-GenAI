import { useTheme } from "../../contexts/ThemeContext";

function categoryHue(name: string): number {
  let hash = 0;
  for (const ch of name) hash = (hash * 31 + (ch.codePointAt(0) ?? 0)) & 0xffff;
  return hash % 360;
}

interface BadgeProps {
  children: React.ReactNode;
  category?: string;
  className?: string;
}

export function Badge({ children, category, className = "" }: Readonly<BadgeProps>) {
  const { theme } = useTheme();
  const hue = category ? categoryHue(category) : 210;

  const style =
    theme === "dark"
      ? {
          background: `hsl(${hue} 60% 20%)`,
          color: `hsl(${hue} 80% 70%)`,
          border: `1px solid hsl(${hue} 60% 30% / 0.4)`,
        }
      : {
          background: `hsl(${hue} 70% 90%)`,
          color: `hsl(${hue} 55% 30%)`,
          border: `1px solid hsl(${hue} 60% 70% / 0.6)`,
        };

  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${className}`}
      style={style}
    >
      {children}
    </span>
  );
}
