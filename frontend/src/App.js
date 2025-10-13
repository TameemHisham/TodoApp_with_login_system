// import { useState } from "react";
import Login from "./Login";

function App() {
  // const [login, setLogin] = useState(false);
  const login = false;
  return <div className="App">{login ? "LOGGED IN!" : <Login />}</div>;
}

export default App;
