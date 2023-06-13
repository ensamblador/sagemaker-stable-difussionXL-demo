
import * as React from "react";
import TopNavigation from "@cloudscape-design/components/top-navigation";


export default (props) => {


  return (

    <TopNavigation
      identity={{
        href: "/",
        title: "Stable Diffusion Sagemaker Demo",
      }}
      utilities={[

      ]}
      i18nStrings={{
        searchIconAriaLabel: "Search",
        searchDismissIconAriaLabel: "Close search",
        overflowMenuTriggerText: "More",
        overflowMenuTitleText: "All",
        overflowMenuBackIconAriaLabel: "Back",
        overflowMenuDismissIconAriaLabel: "Close menu"
      }}
    />
  )
}
