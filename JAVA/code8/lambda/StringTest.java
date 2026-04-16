package lambda;

import java.util.Arrays;
/**
 * 用lambda表达式实现Comparator接口
 * @author He Yongqiang
 *
 */
public class StringTest
{

	public static void main(String[] args)
	{
		String[] sArr=new String[] {"China","America","France","Switzerland "};
		Arrays.sort(sArr, (s1,s2)->s1.length()-s2.length());
		for(String s:sArr)
			System.out.println(s);

	}

}
