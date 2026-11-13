// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "LucasSwiftSmoke",
    products: [.library(name: "LucasSwiftSmoke", targets: ["LucasSwiftSmoke"])],
    targets: [
        .target(name: "LucasSwiftSmoke"),
        .testTarget(name: "LucasSwiftSmokeTests", dependencies: ["LucasSwiftSmoke"])
    ]
)