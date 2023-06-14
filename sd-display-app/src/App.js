import "@cloudscape-design/global-styles/index.css"
import * as React from "react"
import './App.css'
import {
  Routes,
  Route,
  Outlet,

} from "react-router-dom"

import AppLayout from "@cloudscape-design/components/app-layout"
import Home from './Home'
import '@aws-amplify/ui-react/styles.css'
import AppTopNavigation from "./AppTopNavigation"
import Qrcode from "./Qrcode"


const App = () => {



  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Home />} />
        <Route path="/qr" element={<Qrcode  url="http://www.google.com"/>} />
      </Route>
    </Routes>

  )
}

const Layout = (props) => [

  <AppTopNavigation key={1}  />,
  <AppLayout key={2}
    headerSelector="#h"
    toolsHide={true}
    disableContentPaddings={true}
    navigationHide={true}
    footerSelector="#f"
    content={<Outlet />}

  />

]




export default App;
