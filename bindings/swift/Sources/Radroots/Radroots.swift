import RadrootsBindings

public enum Radroots {
  public static var name: String { RadrootsBindings.name() }

  public static func projectName() -> String {
    RadrootsBindings.name()
  }

  public static func printName() {
    RadrootsBindings.printName()
  }
}
