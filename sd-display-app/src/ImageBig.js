
import * as React from "react";

export default ({ im, direction, position }) => {
    const [qr, setQr] = React.useState(null)

    React.useEffect(() => {
        const imgElement = document.getElementById(position + '-image')
        imgElement.style.top = "0px"
        im['qr'].then(val => setQr(val) )
    }, [im])
    return (
        <div className={"single-image-" + im.resolution + (direction ? " down" : " up")}>
            <img id={position + "-image"} src={im.url} />
            {qr ? <div className="qr-code"><img src={qr} /></div>: null}
        </div>)
}
