
import * as React from "react";
import HelpPanel from "@cloudscape-design/components/help-panel";

export default ({ im }) => {
    const [qr, setQr] = React.useState(null)

    React.useEffect(() => {
        im['qr'].then(val => setQr(val))
    }, [im])
    return (
        <div className={"new-image"}>
            <img id="new-image" src={im.url} />

            {qr ? <div className="qr-code-new">

                <HelpPanel footer={<img src={qr} />}
                 header={<h2>Comparte en RRSS con </h2>} >      
                 <div>        
                    <h3>#AWSAIExperience</h3>   </div>    </HelpPanel>

                </div> : null}
        </div>)
}
