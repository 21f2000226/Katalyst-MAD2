import "bootstrap/dist/css/bootstrap.min.css";
import "bootstrap/dist/js/bootstrap.bundle.min.js";
/* importing iosevka ( my fav ) UI font */
import "@fontsource/iosevka-aile/400.css";
import "@fontsource/iosevka-aile/500.css";
import "@fontsource/iosevka-aile/600.css";
import "@fontsource/iosevka-aile/700.css";
import "./assets/katalyst.css";

import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import { fetchMe } from "./services/auth";

const app = createApp(App);
app.use(router);

// restore session from localStorage token before showing pages
fetchMe().finally(() => {
  app.mount("#app");
});
