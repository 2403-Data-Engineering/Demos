object Hello {
    def main(args: Array[String]): Unit = {
        println("Hello, Scala!")
        demo1()

    }

    
    // The above is basically equivalent to this simple Java method:
    // public class Hello {
    //     public static void main(String[] args) {
    //         System.out.println("Hello, Scala!")
    //     }
    // }

    def demo1(): Unit = {
        val x = 10 //VAL for VALUE - this is about the assigned value, it's "const" or "final"
        // x = 11  //this errors out, can't reassign a "val"
        var y: Int = 11
        var z: String = "12"
        println(s"x, y, z: $x, $y, $z")
    }

}


object Thing {
    def demo2(): Unit = {
        //We invoke this like it would be done statically in Java, de-referencing a class name.
        //But it's not actually static, it's a singleton handled by the runtime
        Hello.demo1();
    }
}




