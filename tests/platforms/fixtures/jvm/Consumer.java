import org.radroots.Radroots;

class Consumer {
    public static void main(String[] args) {
        for (int i = 0; i < 10000; i++) {
            if (!Radroots.name().equals("Radroots")) {
                throw new AssertionError("name");
            }
        }
        Radroots.printName();
    }
}
