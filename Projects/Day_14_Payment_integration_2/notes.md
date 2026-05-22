#  SaaS Platform with RBAC + Stripe Payment Integration

A production-ready SaaS backend with Role-Based Access Control (RBAC), organization management, and Stripe subscription billing.

---

##  Features

###  Authentication & Authorization
- JWT-based authentication
- Role-Based Access Control (RBAC)
  - `super_admin` - Full system access
  - `org_admin` - Manage users within organization
  - `user` - Standard user access
- First-login payment activation

###  Payment Integration (Stripe)
- Subscription-based billing
- Multiple pricing plans (Basic, Pro)
- Automatic payment activation on first login
- Webhook handling for payment events
- Payment status dashboard for admins
- Real-time subscription status tracking

###  Organization Management
- Super admin creates organizations
- One org_admin per organization
- Users assigned to organizations
- Org-scoped user management

###  Project & Task Management
- Create/manage projects
- Assign tasks to users
- Subtask support
- Cascading deletes

---
