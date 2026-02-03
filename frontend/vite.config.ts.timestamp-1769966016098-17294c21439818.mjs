// vite.config.ts
import { defineConfig } from "file:///C:/Users/oksbw/OneDrive/Desktop/WealthFam/frontend/node_modules/vite/dist/node/index.js";
import vue from "file:///C:/Users/oksbw/OneDrive/Desktop/WealthFam/frontend/node_modules/@vitejs/plugin-vue/dist/index.mjs";
import path from "path";
import { execSync } from "child_process";
import fs from "fs";
var __vite_injected_original_dirname = "C:\\Users\\oksbw\\OneDrive\\Desktop\\WealthFam\\frontend";
var version = "0.0.0";
try {
  const versionData = JSON.parse(fs.readFileSync(path.resolve(__vite_injected_original_dirname, "../version.json"), "utf-8"));
  version = `${versionData.major}.${versionData.minor}.${versionData.patch}`;
} catch (e) {
  console.warn("Could not read version.json");
}
var build = (process.env.VITE_APP_BUILD || "").trim() || "0000";
if (build === "0000") {
  try {
    build = execSync("git rev-parse master").toString().trim().substring(0, 4);
  } catch (e) {
    console.warn("Could not get git build number from master, trying HEAD...");
    try {
      build = execSync("git rev-parse HEAD").toString().trim().substring(0, 4);
    } catch (e2) {
      console.warn("Could not get git build number, using fallback.");
    }
  }
}
console.log(`--- Building WealthFam v${version} (Build: ${build}) ---`);
var vite_config_default = defineConfig({
  plugins: [vue()],
  define: {
    "__APP_VERSION__": JSON.stringify(version),
    "__APP_BUILD__": JSON.stringify(build)
  },
  resolve: {
    alias: {
      "@": path.resolve(__vite_injected_original_dirname, "./src")
    }
  },
  server: {
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true
      },
      "/parser": {
        target: "http://127.0.0.1:8001",
        changeOrigin: true,
        rewrite: (path2) => path2.replace(/^\/parser/, "/v1")
      }
    }
  }
});
export {
  vite_config_default as default
};
//# sourceMappingURL=data:application/json;base64,ewogICJ2ZXJzaW9uIjogMywKICAic291cmNlcyI6IFsidml0ZS5jb25maWcudHMiXSwKICAic291cmNlc0NvbnRlbnQiOiBbImNvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9kaXJuYW1lID0gXCJDOlxcXFxVc2Vyc1xcXFxva3Nid1xcXFxPbmVEcml2ZVxcXFxEZXNrdG9wXFxcXFdlYWx0aEZhbVxcXFxmcm9udGVuZFwiO2NvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9maWxlbmFtZSA9IFwiQzpcXFxcVXNlcnNcXFxcb2tzYndcXFxcT25lRHJpdmVcXFxcRGVza3RvcFxcXFxXZWFsdGhGYW1cXFxcZnJvbnRlbmRcXFxcdml0ZS5jb25maWcudHNcIjtjb25zdCBfX3ZpdGVfaW5qZWN0ZWRfb3JpZ2luYWxfaW1wb3J0X21ldGFfdXJsID0gXCJmaWxlOi8vL0M6L1VzZXJzL29rc2J3L09uZURyaXZlL0Rlc2t0b3AvV2VhbHRoRmFtL2Zyb250ZW5kL3ZpdGUuY29uZmlnLnRzXCI7Ly8gQHRzLW5vY2hlY2tcclxuaW1wb3J0IHsgZGVmaW5lQ29uZmlnIH0gZnJvbSAndml0ZSdcclxuaW1wb3J0IHZ1ZSBmcm9tICdAdml0ZWpzL3BsdWdpbi12dWUnXHJcbmltcG9ydCBwYXRoIGZyb20gJ3BhdGgnXHJcbmltcG9ydCB7IGV4ZWNTeW5jIH0gZnJvbSAnY2hpbGRfcHJvY2VzcydcclxuaW1wb3J0IGZzIGZyb20gJ2ZzJ1xyXG5cclxuLy8gUmVhZCB2ZXJzaW9uLmpzb24gZnJvbSByb290XHJcbmxldCB2ZXJzaW9uID0gJzAuMC4wJ1xyXG50cnkge1xyXG4gIGNvbnN0IHZlcnNpb25EYXRhID0gSlNPTi5wYXJzZShmcy5yZWFkRmlsZVN5bmMocGF0aC5yZXNvbHZlKF9fZGlybmFtZSwgJy4uL3ZlcnNpb24uanNvbicpLCAndXRmLTgnKSlcclxuICB2ZXJzaW9uID0gYCR7dmVyc2lvbkRhdGEubWFqb3J9LiR7dmVyc2lvbkRhdGEubWlub3J9LiR7dmVyc2lvbkRhdGEucGF0Y2h9YFxyXG59IGNhdGNoIChlKSB7XHJcbiAgY29uc29sZS53YXJuKCdDb3VsZCBub3QgcmVhZCB2ZXJzaW9uLmpzb24nKVxyXG59XHJcblxyXG4vLyBHZXQgbGF0ZXN0IDQgZGlnaXRzIG9mIG1hc3RlciBjb21taXQgb3IgZnJvbSBlbnZpcm9ubWVudFxyXG5sZXQgYnVpbGQgPSAocHJvY2Vzcy5lbnYuVklURV9BUFBfQlVJTEQgfHwgJycpLnRyaW0oKSB8fCAnMDAwMCdcclxuXHJcbmlmIChidWlsZCA9PT0gJzAwMDAnKSB7XHJcbiAgdHJ5IHtcclxuICAgIGJ1aWxkID0gZXhlY1N5bmMoJ2dpdCByZXYtcGFyc2UgbWFzdGVyJykudG9TdHJpbmcoKS50cmltKCkuc3Vic3RyaW5nKDAsIDQpXHJcbiAgfSBjYXRjaCAoZSkge1xyXG4gICAgY29uc29sZS53YXJuKCdDb3VsZCBub3QgZ2V0IGdpdCBidWlsZCBudW1iZXIgZnJvbSBtYXN0ZXIsIHRyeWluZyBIRUFELi4uJylcclxuICAgIHRyeSB7XHJcbiAgICAgIGJ1aWxkID0gZXhlY1N5bmMoJ2dpdCByZXYtcGFyc2UgSEVBRCcpLnRvU3RyaW5nKCkudHJpbSgpLnN1YnN0cmluZygwLCA0KVxyXG4gICAgfSBjYXRjaCAoZTIpIHtcclxuICAgICAgY29uc29sZS53YXJuKCdDb3VsZCBub3QgZ2V0IGdpdCBidWlsZCBudW1iZXIsIHVzaW5nIGZhbGxiYWNrLicpXHJcbiAgICB9XHJcbiAgfVxyXG59XHJcblxyXG5jb25zb2xlLmxvZyhgLS0tIEJ1aWxkaW5nIFdlYWx0aEZhbSB2JHt2ZXJzaW9ufSAoQnVpbGQ6ICR7YnVpbGR9KSAtLS1gKVxyXG5cclxuLy8gaHR0cHM6Ly92aXRlanMuZGV2L2NvbmZpZy9cclxuZXhwb3J0IGRlZmF1bHQgZGVmaW5lQ29uZmlnKHtcclxuICBwbHVnaW5zOiBbdnVlKCldLFxyXG4gIGRlZmluZToge1xyXG4gICAgJ19fQVBQX1ZFUlNJT05fXyc6IEpTT04uc3RyaW5naWZ5KHZlcnNpb24pLFxyXG4gICAgJ19fQVBQX0JVSUxEX18nOiBKU09OLnN0cmluZ2lmeShidWlsZClcclxuICB9LFxyXG4gIHJlc29sdmU6IHtcclxuICAgIGFsaWFzOiB7XHJcbiAgICAgICdAJzogcGF0aC5yZXNvbHZlKF9fZGlybmFtZSwgJy4vc3JjJylcclxuICAgIH1cclxuICB9LFxyXG4gIHNlcnZlcjoge1xyXG4gICAgcHJveHk6IHtcclxuICAgICAgJy9hcGknOiB7XHJcbiAgICAgICAgdGFyZ2V0OiAnaHR0cDovLzEyNy4wLjAuMTo4MDAwJyxcclxuICAgICAgICBjaGFuZ2VPcmlnaW46IHRydWUsXHJcbiAgICAgIH0sXHJcbiAgICAgICcvcGFyc2VyJzoge1xyXG4gICAgICAgIHRhcmdldDogJ2h0dHA6Ly8xMjcuMC4wLjE6ODAwMScsXHJcbiAgICAgICAgY2hhbmdlT3JpZ2luOiB0cnVlLFxyXG4gICAgICAgIHJld3JpdGU6IChwYXRoKSA9PiBwYXRoLnJlcGxhY2UoL15cXC9wYXJzZXIvLCAnL3YxJyksXHJcbiAgICAgIH1cclxuICAgIH1cclxuICB9XHJcbn0pXHJcbiJdLAogICJtYXBwaW5ncyI6ICI7QUFDQSxTQUFTLG9CQUFvQjtBQUM3QixPQUFPLFNBQVM7QUFDaEIsT0FBTyxVQUFVO0FBQ2pCLFNBQVMsZ0JBQWdCO0FBQ3pCLE9BQU8sUUFBUTtBQUxmLElBQU0sbUNBQW1DO0FBUXpDLElBQUksVUFBVTtBQUNkLElBQUk7QUFDRixRQUFNLGNBQWMsS0FBSyxNQUFNLEdBQUcsYUFBYSxLQUFLLFFBQVEsa0NBQVcsaUJBQWlCLEdBQUcsT0FBTyxDQUFDO0FBQ25HLFlBQVUsR0FBRyxZQUFZLEtBQUssSUFBSSxZQUFZLEtBQUssSUFBSSxZQUFZLEtBQUs7QUFDMUUsU0FBUyxHQUFHO0FBQ1YsVUFBUSxLQUFLLDZCQUE2QjtBQUM1QztBQUdBLElBQUksU0FBUyxRQUFRLElBQUksa0JBQWtCLElBQUksS0FBSyxLQUFLO0FBRXpELElBQUksVUFBVSxRQUFRO0FBQ3BCLE1BQUk7QUFDRixZQUFRLFNBQVMsc0JBQXNCLEVBQUUsU0FBUyxFQUFFLEtBQUssRUFBRSxVQUFVLEdBQUcsQ0FBQztBQUFBLEVBQzNFLFNBQVMsR0FBRztBQUNWLFlBQVEsS0FBSyw0REFBNEQ7QUFDekUsUUFBSTtBQUNGLGNBQVEsU0FBUyxvQkFBb0IsRUFBRSxTQUFTLEVBQUUsS0FBSyxFQUFFLFVBQVUsR0FBRyxDQUFDO0FBQUEsSUFDekUsU0FBUyxJQUFJO0FBQ1gsY0FBUSxLQUFLLGlEQUFpRDtBQUFBLElBQ2hFO0FBQUEsRUFDRjtBQUNGO0FBRUEsUUFBUSxJQUFJLDJCQUEyQixPQUFPLFlBQVksS0FBSyxPQUFPO0FBR3RFLElBQU8sc0JBQVEsYUFBYTtBQUFBLEVBQzFCLFNBQVMsQ0FBQyxJQUFJLENBQUM7QUFBQSxFQUNmLFFBQVE7QUFBQSxJQUNOLG1CQUFtQixLQUFLLFVBQVUsT0FBTztBQUFBLElBQ3pDLGlCQUFpQixLQUFLLFVBQVUsS0FBSztBQUFBLEVBQ3ZDO0FBQUEsRUFDQSxTQUFTO0FBQUEsSUFDUCxPQUFPO0FBQUEsTUFDTCxLQUFLLEtBQUssUUFBUSxrQ0FBVyxPQUFPO0FBQUEsSUFDdEM7QUFBQSxFQUNGO0FBQUEsRUFDQSxRQUFRO0FBQUEsSUFDTixPQUFPO0FBQUEsTUFDTCxRQUFRO0FBQUEsUUFDTixRQUFRO0FBQUEsUUFDUixjQUFjO0FBQUEsTUFDaEI7QUFBQSxNQUNBLFdBQVc7QUFBQSxRQUNULFFBQVE7QUFBQSxRQUNSLGNBQWM7QUFBQSxRQUNkLFNBQVMsQ0FBQ0EsVUFBU0EsTUFBSyxRQUFRLGFBQWEsS0FBSztBQUFBLE1BQ3BEO0FBQUEsSUFDRjtBQUFBLEVBQ0Y7QUFDRixDQUFDOyIsCiAgIm5hbWVzIjogWyJwYXRoIl0KfQo=
