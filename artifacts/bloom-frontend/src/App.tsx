import { Switch, Route, Router as WouterRouter } from "wouter";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import NotFound from "@/pages/not-found";

import { LanguageProvider } from "@/i18n";
import Layout from "@/components/layout";
import Dashboard from "@/pages/dashboard";
import Generate from "@/pages/generate";
import Lessons from "@/pages/lessons";
import LessonDetail from "@/pages/lesson-detail";
import Profiles from "@/pages/profiles";
import Curriculum from "@/pages/curriculum";
import Knowledge from "@/pages/knowledge";
import Classify from "@/pages/classify";

const queryClient = new QueryClient();

function Router() {
  return (
    <Layout>
      <Switch>
        <Route path="/" component={Dashboard} />
        <Route path="/generate" component={Generate} />
        <Route path="/lessons" component={Lessons} />
        <Route path="/lessons/:id" component={LessonDetail} />
        <Route path="/profiles" component={Profiles} />
        <Route path="/curriculum" component={Curriculum} />
        <Route path="/knowledge" component={Knowledge} />
        <Route path="/classify" component={Classify} />
        <Route component={NotFound} />
      </Switch>
    </Layout>
  );
}

function App() {
  return (
    <LanguageProvider>
      <QueryClientProvider client={queryClient}>
        <TooltipProvider>
          <WouterRouter base={import.meta.env.BASE_URL.replace(/\/$/, "")}>
            <Router />
          </WouterRouter>
          <Toaster />
        </TooltipProvider>
      </QueryClientProvider>
    </LanguageProvider>
  );
}

export default App;
