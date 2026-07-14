import { createRouter, createWebHistory } from "vue-router";
import { getToken } from "../api/client";
import { authState, dashboardPathForRole, fetchMe } from "../services/auth";

const studentSidebar = [
  { to: "/student/drives", label: "Browse drives" },
  { to: "/student/applications", label: "My applications" },
];

const companySidebar = [
  { to: "/company/drives", label: "My drives" },
];

const routes = [
  // Public landing for guests. Signed-in users are sent to their dashboard below.

  {
    path: "/",
    name: "home",
    component: () => import("../views/HomeView.vue"),
  },
  { path: "/login", name: "login", component: () => import("../views/LoginView.vue"), meta: { guest: true } },
  { path: "/register", name: "register", component: () => import("../views/RegisterView.vue"), meta: { guest: true } },
  {
    path: "/admin",
    name: "admin",
    component: () => import("../views/admin/AdminDashboard.vue"),
    meta: { requiresAuth: true, role: "admin" },
  },

  {
    path: "/student",
    component: () => import("../components/RoleLayout.vue"),
    meta: { requiresAuth: true, role: "student", sidebarLinks: studentSidebar },
    children: [
      { path: "", redirect: { name: "student-drives" } },
      // old /jobs urls still work
      { path: "jobs", redirect: { name: "student-drives" } },
      {
        path: "drives",
        name: "student-drives",
        component: () => import("../views/student/StudentJobs.vue"),
      },
      {
        path: "drives/:id",
        name: "student-drive",
        component: () => import("../views/student/StudentDriveDetail.vue"),
      },
      {
        path: "applications",
        name: "student-applications",
        component: () => import("../views/student/StudentApplications.vue"),
      },
      {
        path: "profile",
        name: "student-profile",
        component: () => import("../views/student/StudentProfile.vue"),
      },
    ],
  },

  {
    path: "/company",
    component: () => import("../components/RoleLayout.vue"),
    meta: { requiresAuth: true, role: "company", sidebarLinks: companySidebar },
    children: [
      { path: "", redirect: { name: "company-drives" } },
      { path: "jobs", redirect: { name: "company-drives" } },
      { path: "jobs/:id", redirect: (to) => ({ name: "company-drive", params: { id: to.params.id } }) },
      {
        path: "drives",
        name: "company-drives",
        component: () => import("../views/company/CompanyDashboard.vue"),
      },

      {
        path: "drives/:id",
        name: "company-drive",
        component: () => import("../views/company/CompanyJobDetail.vue"),
      },

      {
        path: "profile",
        name: "company-profile",
        component: () => import("../views/company/CompanyProfile.vue"),
      },

    ],
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

function roleHome(role) {
  return dashboardPathForRole(role) || "/login";
}

router.beforeEach(async (to) => {
  if (getToken() && !authState.user) {
    await fetchMe();
  }

  // if Signed in, we will not be showing the landing page, redirect to dashboard
  if (to.name === "home" || to.path === "/") {
    if (authState.user) {
      return roleHome(authState.user.role);
    }
  }

  const needsAuth = to.matched.some((r) => r.meta.requiresAuth);
  if (needsAuth && !getToken()) {
    return { name: "login", query: { redirect: to.fullPath } };
  }

  const neededRole = [...to.matched].map((r) => r.meta.role).find(Boolean);
  if (neededRole && authState.user?.role !== neededRole) {
    if (authState.user) return roleHome(authState.user.role);
    return { name: "login" };
  }

  if (to.meta.guest && getToken() && authState.user) {
    return roleHome(authState.user.role);
  }

  return true;
});

export default router;
