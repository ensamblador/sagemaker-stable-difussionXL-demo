import QRCode from 'qrcode'

export const  generateQR = async text => {
    try {
        const qrBinary = await QRCode.toDataURL(text)
        return qrBinary
    } catch (err) {
        console.error(err)
        return null
    }
}