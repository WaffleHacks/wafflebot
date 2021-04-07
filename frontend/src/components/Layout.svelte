<style lang="scss">
  /* Sidebar */
  .sidebar {
    position: fixed;
    top: 0;
    bottom: 0;
    left: 0;
    z-index: 100;
    padding: 48px 0 0;
    box-shadow: inset -1px 0 0 rgba(0, 0, 0, 0.1);
  }

  @media (max-width: 767.98px) {
    .sidebar {
      top: 5rem;
    }
  }

  .sidebar .nav-link {
    font-weight: 500;
    color: #333;
  }

  .sidebar .nav-link.active {
    color: #007bff;
  }

  .sidebar-heading {
    font-size: 0.75rem;
    text-transform: uppercase;
  }

  /* Navbar */
  .navbar-brand {
    padding-top: 0.75rem;
    padding-bottom: 0.75rem;
    font-size: 1rem;
    background-color: rgba(0, 0, 0, 0.25);
    box-shadow: inset -1px 0 0 rgba(0, 0, 0, 0.25);
  }

  .navbar .navbar-toggler {
    top: 0.25rem;
    right: 1rem;
  }
</style>

<script>
  import page from "page";
  import { icons } from "feather-icons";
  import { User } from "../api";
  import { SVG_ATTRS } from "../constants";
  import { activeRoute } from "../router/Router.svelte";

  // The sidebar navigation items
  const NAVIGATION = [
    {
      title: "General",
      links: [
        {
          icon: "home",
          name: "Home",
          to: "/",
        },
        {
          icon: "mail",
          name: "Canned Responses",
          to: "/canned-responses",
        },
        {
          icon: "settings",
          name: "Settings",
          to: "/settings",
        }
      ],
    },
    {
      title: "Ticketing",
      links: [
        {
          icon: "layers",
          name: "Tickets",
          to: "/tickets",
        },
        {
          icon: "list",
          name: "Categories",
          to: "/tickets/categories",
        }
      ],
    }
  ];

  // Logout the current user
  async function onLogout() {
    // Logout the user
    await User.logout();

    // Redirect to the login page
    page.redirect("/login");
  }
</script>

<header class="navbar navbar-dark sticky-top bg-dark flex-md-nowrap p-0 shadow">
  <a class="navbar-brand col-md-3 col-lg-2 me-0 px-3" href="/">WaffleBot</a>
  <button class="navbar-toggler position-absolute d-md-none collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#sidebarMenu" aria-controls="sidebarMenu" aria-expanded="false" aria-label="Toggle navigation">
    <span class="navbar-toggler-icon"></span>
  </button>
  <ul class="navbar-nav px-3">
    <li class="nav-item text-nowrap">
      <button class="nav-link btn btn-link" on:click={onLogout}>Log out</button>
    </li>
  </ul>
</header>

<div class="container-fluid">
  <div class="row">
    <nav id="sidebarMenu" class="col-md-3 col-lg-2 d-md-block bg-light sidebar collapse">
      <div class="position-sticky pt-3">
        {#each NAVIGATION as {title, links}}
          <h6 class="sidebar-heading d-flex justify-content-between align-items-center px-3 mt-4 mb-1 text-muted">
            {title}
          </h6>

          <ul class="nav flex-column">
            {#each links as {name, icon, to}}
              <li class="nav-item">
                <a class="nav-link" class:active={$activeRoute.path === to} aria-current="{$activeRoute.path === to}" class:disabled={$activeRoute.path === to} href="{to}">
                  {@html icons[icon].toSvg(SVG_ATTRS)}
                  {name}
                </a>
              </li>
            {/each}
          </ul>
        {/each}
      </div>
    </nav>

    <main class="col-md-9 ms-sm-auto col-lg-10 px-md-4">
      <slot/>
    </main>
  </div>
</div>
