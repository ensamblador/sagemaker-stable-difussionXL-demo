import * as React from "react";
import "@cloudscape-design/global-styles/index.css"
import QRCode from 'qrcode'


export default ({ url }) => {
    const [qr, setQr] = React.useState(null)

    const generateQR = async text => {
        try {
            const qrBinary = await QRCode.toDataURL(text)
            //console.log(qrBinary)
            setQr(qrBinary)
        } catch (err) {
            console.error(err)
        }
    }

    React.useEffect(() => {

        generateQR(url)

    }, [url]);


    return (
        <div>
            {qr ? <img src={qr} />: null}
        </div>
    )

}




