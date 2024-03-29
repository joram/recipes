import './App.css';
import 'semantic-ui-css/semantic.min.css'
import "pure-react-carousel/dist/react-carousel.es.css";
import RecipeSearch from "./components/recipeSearch";
import {Link, Outlet, Route, Routes} from "react-router-dom";
import React from "react";
import RecipePage from "./pages/RecipePage";
import {Menu} from "semantic-ui-react";
import HomePage from "./pages/HomePage";
import WeekPlanPage from "./pages/WeeklyPlan";
import SignIn from "./components/loginButton";

function Layout() {
    return (
        <div>
            <Menu attached="top">
                <Menu.Item>
                    <Link to="/">Random Recipe</Link>
                </Menu.Item>
                <Menu.Item>
                    <Link to="/plan">Plan Meals</Link>
                </Menu.Item>
                <Menu.Item>
                    <RecipeSearch/>
                </Menu.Item>
                <Menu.Item position="right">
                    <SignIn />
                </Menu.Item>
            </Menu>
            <Outlet />
        </div>
    );
}


function App() {
  return (
    <div className="App">
        <Routes>
            <Route path="/" element={<Layout />}>
                <Route index element={<HomePage />} />
                <Route path="/plan" element={<WeekPlanPage/>} />
                <Route path="/recipe/:recipeTitle" element={<RecipePage />} />
            </Route>
        </Routes>
    </div>
  );
}

export default App;
