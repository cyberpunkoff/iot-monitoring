import { type RouteConfig, index, route } from "@react-router/dev/routes";

export default [
  route("", "components/Layout.tsx", [
    index("routes/home.tsx"),
    route("historical", "routes/historical.tsx"),
    route("statistics", "routes/statistics.tsx"),
    route("metadata", "routes/metadata.tsx"),
    route("admin", "routes/admin.tsx"),
    route("login", "routes/login.tsx"),
    route("register", "routes/register.tsx")
  ])
] satisfies RouteConfig;
