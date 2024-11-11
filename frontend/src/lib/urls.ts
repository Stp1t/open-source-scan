export function parseGithubUrl(url: string): undefined | URL {
    let result: URL
    try {
        //todo: add github search / autocomplete
        result = new URL(url)
    } catch (e) {
        console.error(e)
        return undefined
    }
    if (result.hostname === "github.com") {
        const paths = result.pathname.split("/")
        if (paths.length !== 2) {
            result.pathname = `${paths[1]}/${paths[2]}` // index 0 is empty string
        }
        result.hash = ""
        result.search = ""
    }
    return result
}