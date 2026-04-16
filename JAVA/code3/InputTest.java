import java.util.*;

public class InputTest
{
	public static void main(String[] args)
	{
		Scanner in = new Scanner(System.in);

		// get first input
		System.out.println("What is your name? ");
		String name = in.nextLine();

		// get second input
		System.out.print("How old are you? ");
		int age = 0;

		while (!in.hasNextInt())
		{
			System.out.println("You shoud input a integer:");
			in.nextLine();  
		}

		if (in.hasNextInt())
			age = in.nextInt();

		// display output on console
		System.out.println("Hello, " + name + ". Next year, you'll be " + (age + 1));
	}
}
