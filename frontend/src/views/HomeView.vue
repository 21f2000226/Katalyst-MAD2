<script setup>
/**
 * Public landing at /. 
 */
</script>

<template>
  <!-- Guest landing page-->
  <div class="bg-primary text-white py-5">
    <div class="container py-4">
      <div class="row align-items-center">
        <div class="col-lg-7">
          <span class="badge bg-white text-primary fw-semibold mb-3 px-3 py-2">Now open for 2025-26</span>
          <h1 class="display-4 fw-bold mb-3">Your campus placement,<br />streamlined.</h1>
          <p class="lead mb-4 text-white-75">
            Katalyst connects students with top companies, lets institutes manage the process end-to-end,
            and gives companies a direct line to fresh talent.
          </p>

          <div class="d-flex flex-wrap gap-3">
            <router-link to="/register?role=student" class="btn btn-light btn-lg px-4 fw-semibold">
              Get started as Student
            </router-link>
            <router-link to="/login" class="btn btn-outline-light btn-lg px-4">
              Log in
            </router-link>
          </div>

        </div>
        <div class="col-lg-5 text-center d-none d-lg-block">
          <div style="font-size: 8rem; line-height: 1; opacity: 0.25">🎯</div>
        </div>
      </div>
    </div>
  </div>

  <div class="container py-5">

    <h2 class="fw-bold text-center mb-5">Built for everyone in the process</h2>
    <div class="row g-4">
      <div class="col-md-4">
        <div class="card h-100 border-0 shadow-sm">
          <div class="card-body text-center p-4">
            <div class="fs-1 mb-3">👤</div>
            <h5 class="fw-bold">For Students</h5>
            <p class="text-muted">
              Build your profile, browse placement drives from approved companies, apply in one click, and
              track your application status - all in one dashboard.
            </p>
            <router-link to="/register?role=student" class="btn btn-outline-primary btn-sm mt-2">
              Register as Student
            </router-link>
          </div>
        </div>
      </div>

      <div class="col-md-4">
        <div class="card h-100 border-0 shadow-sm">
          <div class="card-body text-center p-4">
            <div class="fs-1 mb-3">🏢</div>
            <h5 class="fw-bold">For Companies</h5>
            <p class="text-muted">
              Register, get approved by the institute, post placement drives, review applications,
              shortlist candidates, and mark placements.
            </p>
            <router-link to="/register?role=company" class="btn btn-outline-primary btn-sm mt-2">
              Register as Company
            </router-link>
          </div>
        </div>
      </div>

      <div class="col-md-4">
        <div class="card h-100 border-0 shadow-sm">
          <div class="card-body text-center p-4">
            <div class="fs-1 mb-3">⚙️</div>
            <h5 class="fw-bold">For the Institute</h5>
            <p class="text-muted">
              Admin dashboard to approve companies and drives, manage student and company records,
              and get a live overview of all placements.
            </p>
            <router-link to="/login" class="btn btn-outline-secondary btn-sm mt-2">
              Admin Login
            </router-link>
          </div>
        </div>
      </div>

    </div>
  </div>

  <div class="bg-light border-top border-bottom py-5">
    <div class="container">
      <h2 class="fw-bold text-center mb-5">How it works</h2>
      
      <div class="row g-4 text-center">
        <div class="col-6 col-md-3">
          <div
            class="rounded-circle bg-primary text-white fw-bold d-inline-flex align-items-center justify-content-center mb-3"
            style="width: 48px; height: 48px; font-size: 1.1rem"
          >
            1
          </div>
          <div class="fw-semibold mb-1">Sign up</div>
          <div class="text-muted small">Choose your role - student or company - and create your account.</div>
        </div>
        <div class="col-6 col-md-3">
          <div
            class="rounded-circle bg-primary text-white fw-bold d-inline-flex align-items-center justify-content-center mb-3"
            style="width: 48px; height: 48px; font-size: 1.1rem"
          >
            2
          </div>
          <div class="fw-semibold mb-1">Get approved</div>
          <div class="text-muted small">Companies are verified by the institute before they can post drives.</div>
        </div>
        <div class="col-6 col-md-3">
          <div
            class="rounded-circle bg-primary text-white fw-bold d-inline-flex align-items-center justify-content-center mb-3"
            style="width: 48px; height: 48px; font-size: 1.1rem"
          >
            3
          </div>
          <div class="fw-semibold mb-1">Browse &amp; Apply</div>
          <div class="text-muted small">Students browse approved drives and apply with a single click.</div>
        </div>
        <div class="col-6 col-md-3">
          <div
            class="rounded-circle bg-primary text-white fw-bold d-inline-flex align-items-center justify-content-center mb-3"
            style="width: 48px; height: 48px; font-size: 1.1rem"
          >
            4
          </div>
          <div class="fw-semibold mb-1">Get placed</div>
          <div class="text-muted small">Companies shortlist, select, and the placement is recorded on the portal.</div>
        </div>
        
      </div>
    </div>
  </div>

  <div class="container py-5 text-center">
    <h3 class="fw-bold mb-2">Ready to get started?</h3>
    <p class="text-muted mb-4">Join Katalyst today - it takes less than a minute to register.</p>
    <router-link to="/register" class="btn btn-primary btn-lg px-5">Create your account</router-link>
  </div>
</template>

