/** @type {import('tailwindcss').Config} */

import defaultTheme from "tailwindcss/defaultTheme";

export default {
  content: ["./index.html", "./src/**/*.{vue,js,ts,jsx,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        hs: ["HS유지체", ...defaultTheme.fontFamily.sans],
        makgeolli: ["MAKGEOLLI", ...defaultTheme.fontFamily.sans],
      },
      backgroundImage: {
        "fairytail-image": "url('/src/assets/background.webp')",
      },
      animation: {
        shake: "shake 1s ease-in-out infinite", // 애니메이션 이름과 지속 시간
      },
      keyframes: {
        shake: {
          "0%, 100%": { transform: "translateX(0)" },
          "25%": { transform: "translateX(-1px)" },
          "50%": { transform: "translateX(1px)" },
          "75%": { transform: "translateX(-1px)" },
        },
      },
      cursor: {
        pointer: 'url("/src/assets/icons/fairy.png"), pointer',
      },
    },
  },
  plugins: [],
};
