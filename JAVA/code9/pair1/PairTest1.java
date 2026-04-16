package pair1;

import java.util.Arrays;


public class PairTest1
{
	public static void main(String[] args)
	{
		String[] words = { "Mary", "had", "a", "little", "lamb", "82328232" };
		Pair<String> mm = ArrayAlg.minmax(words);
		System.out.println("min = " + mm.getFirst());
		System.out.println("max = " + mm.getSecond());

		String middle=ArrayAlg.getMiddle(words);
		System.out.println("middle = "+middle);
//		for(String s:words)
//		   System.out.println(s);
		double middleDouble=ArrayAlg.getMiddle(35.3, 4.0, 12.0, 9.1, -9.0);
		System.out.println("middleDouble = "+middleDouble);		
		
	}
}

class ArrayAlg
{
	
	public static Pair<String> minmax(String[] a)
	{
		if (a == null || a.length == 0)
			return null;
		String min = a[0];
		String max = a[0];
		for (int i = 1; i < a.length; i++)
		{
			if (min.compareTo(a[i]) > 0)
				min = a[i];
			if (max.compareTo(a[i]) < 0)
				max = a[i];
		}
		return new Pair<>(min, max);
	}

	public static <T> T getMiddle(T... a)
	{
		T[] b=a.clone();
		Arrays.sort(b);
		return b[b.length / 2];
	}

}
