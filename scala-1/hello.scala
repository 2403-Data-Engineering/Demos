object Hello {
    def main(args: Array[String]): Unit = {
        println("Hello, Scala!")
        demo1()
        DemoObject.stringInterpOne()
        DemoObject.stringInterpTwo()
        DemoObject.stringInterpThree()
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




// Statement vs expression?
//If is a statement, not an expression in most languages
// What is the special thing like "if" that allows predicate assignment? Ternary operator
// In Scala there is no ternary operator... we don't need it... why? In Scala "If"s are expressions!



// Expressions resolve to a value
// Invoking functions/methods are expressions
// math: 2+2, 2-3, + - / * %
// And also: if statements can be expressions


// val status = if (score >= 60) "pass" else "fail" //This is effectively a ternary expression

// val result = {
//   val a = 10
//   val b = 20
//   a + b      // This is the value of the block
// }


object DemoObject {
    def stringInterpOne(): Unit = {
        val name = "Alice"
        val fullName = "Alice" + " " + "Smith"
        val greeting = s"Hello, $name, your full name is: $fullName"
        println(greeting)
    }

    def stringInterpTwo(): Unit = {
        val price: Double = 3.14159
        println(f"Price: $$$price%.2f")
    }

    def stringInterpThree(): Unit = {
        val testVal = "test"
        val multiLineString = s"""This is a multi-line 
string. The whitespace and newline
characters are maintained.
$testVal
"""
        println(multiLineString)
    }

}



