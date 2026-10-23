// Lists the on-screen windows of one app (default PixInsight) as JSON lines: id x y w h layer title. Used by capture_run.py.
import CoreGraphics
import Foundation
let owner = CommandLine.arguments.count > 1 ? CommandLine.arguments[1] : "PixInsight"
let all = CommandLine.arguments.count > 2 && CommandLine.arguments[2] == "all"
let list = CGWindowListCopyWindowInfo(all ? [.optionAll] : [.optionOnScreenOnly, .excludeDesktopElements], kCGNullWindowID) as! [[String: Any]]
for w in list.reversed() {                       // back to front
    guard (w[kCGWindowOwnerName as String] as? String) == owner else { continue }
    let b = w[kCGWindowBounds as String] as! [String: Any]
    let id = w[kCGWindowNumber as String] as! Int, layer = w[kCGWindowLayer as String] as! Int
    let name = (w[kCGWindowName as String] as? String) ?? ""
    print("\(id)\t\(b["X"]!)\t\(b["Y"]!)\t\(b["Width"]!)\t\(b["Height"]!)\t\(layer)\t\(name)")
}
